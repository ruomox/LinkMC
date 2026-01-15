import asyncio
import json
import logging
import uuid
from typing import Callable, Awaitable, Optional, Dict, Any

# 引入最新的 websockets 客户端模块
from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed
from websockets import ClientConnection

# 导入配置文件
import config

# 配置日志
logger = logging.getLogger("McPluginClient")

# --- 类型定义 ---
# 回调函数类型：接收 dict，返回 Awaitable[None]
MessageHandlerType = Callable[[Dict[str, Any]], Awaitable[None]]

# --- 全局状态管理 ---
# MC 插件消息接收回调
_mcplugin_message_handler: Optional[MessageHandlerType] = None

# 活跃的 MC 插件连接对象
_active_mc_ws: Optional[ClientConnection] = None

# 挂起的 API 请求字典 {echo_uuid: asyncio.Future}
_pending_api_requests: Dict[str, asyncio.Future[Dict[str, Any]]] = {}


# ==========================================
# 对外公共接口 (Public API)
# ==========================================

def register_mcplugin_message_handler(handler: MessageHandlerType):
    """
    [接口] 注册 MC 插件消息处理函数 (业务逻辑入口)
    """
    global _mcplugin_message_handler
    _mcplugin_message_handler = handler
    logger.info("已注册 MC 插件消息处理回调函数。")

def _render_template(obj: Any, **kwargs) -> Any:
    """
    递归渲染 JSON 模板：
    - str: 使用 format(**kwargs)
    - list/dict: 递归处理内部元素
    - 其它 JSON 类型: 原样返回
    """
    if isinstance(obj, str):
        try:
            return obj.format(**kwargs)
        except KeyError as e:
            missing = e.args[0]
            raise ValueError(f"Missing required parameter '{missing}'") from e

    if isinstance(obj, list):
        return [_render_template(x, **kwargs) for x in obj]

    if isinstance(obj, dict):
        return {k: _render_template(v, **kwargs) for k, v in obj.items()}

    return obj

# McPlugin API配置 来自 config
def build_mc_payload(kind: str, **kwargs) -> dict:
    try:
        proto = config.MCPLUGIN_PROTOCOL[kind]
    except KeyError:
        raise ValueError(f"Unknown MCPLUGIN_PROTOCOL kind: {kind}")

    # 协议结构校验
    if "api" not in proto or "data" not in proto:
        raise ValueError(
            f"Invalid MCPLUGIN_PROTOCOL definition for kind '{kind}', "
            f"must contain 'api' and 'data'"
        )

    try:
        # 递归渲染整个 data 结构
        data = _render_template(proto["data"], **kwargs)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(
            f"Missing required parameter '{missing}' for protocol kind '{kind}'"
        ) from e

    payload = {
        "api": proto["api"],
        "data": data,
    }

    if config.MCPLUGIN_ENABLE_ECHO:
        payload["echo"] = kwargs.get("echo")

    return payload

async def call_mc_plugin_api(kind: str, params: Optional[Dict] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    [接口] 调用 MC 插件 API 并异步等待响应结果 (核心功能)
    注意：需要确认所使用的 MC 插件协议是否支持 'echo' 字段回调机制。
    """
    if not config.MCPLUGIN_ENABLE_ECHO:
        raise RuntimeError(
            "MC Plugin echo-response is disabled in config "
            "(MCPLUGIN_ENABLE_ECHO = False)"
        )
    request_uuid = str(uuid.uuid4())

    # 根据 config 内配置的 json 发送
    payload = build_mc_payload(
        kind,
        **(params or {}),
        echo=request_uuid
    )

    loop = asyncio.get_running_loop()
    future = loop.create_future()
    _pending_api_requests[request_uuid] = future

    try:
        # 复用底层的发送实现
        await _send_to_mc_impl(payload)
        logger.debug(f"[API调用] 已发送请求到 MC: {kind}, echo: {request_uuid}")

        # 等待响应
        response = await asyncio.wait_for(future, timeout)
        return response

    except asyncio.TimeoutError:
        logger.error(f"[API调用失败] 请求 MC 超时 ({timeout}s): {kind}, echo: {request_uuid}")
        raise
    except Exception as e:
        logger.error(f"[API调用失败] 发送请求到 MC 时出错: {e}, echo: {request_uuid}")
        raise ConnectionError(f"Failed to send API request to MC: {e}") from e
    finally:
        _pending_api_requests.pop(request_uuid, None)


async def send_to_mc_async_notification(kind: str, **kwargs) -> bool:
    """
    [接口] 发送异步通知数据到 MC 插件 (不等待响应)
    """
    try:
        # 异步通知禁止 echo
        kwargs.pop("echo", None)
        payload = build_mc_payload(kind, **kwargs)
        await _send_to_mc_impl(payload)
        return True
    except Exception as e:
        logger.error(f"[异步发送失败] kind={kind}, error={e}", exc_info=True)
        return False


# ==========================================
# 内部实现细节 (Internal Implementation)
# ==========================================

async def _send_to_mc_impl(data_dict: dict):
    """
    [内部] 底层发送实现
    """
    # 检查连接是否存在且处于打开状态
    if _active_mc_ws is None:
        raise ConnectionError("MC Plugin connection is not active.")

    try:
        json_str = json.dumps(data_dict, ensure_ascii=False)
        await _active_mc_ws.send(json_str)
        if config.DEBUG_MODE and 'echo' not in data_dict:
            logger.debug(f"[中枢 -> MC插件(通知)] 已发送: {json_str[:150]}...")
    except Exception as e:
        logger.error(f"[底层发送失败] 发送数据到 MC 插件出错: {e}")
        raise


async def run_client_task():
    """
    [内部] 客户端主任务：维护连接和监听消息
    """
    global _active_mc_ws

    extra_headers = {
        "x-self-name": config.McPlugin_SELF_NAME,
        "Authorization": f"Bearer {config.McPlugin_WS_TOKEN}"
    }

    logger.info(f"[服务启动] MC 插件客户端任务正在初始化，目标: {config.McPlugin_WS_URI}")

    # 断线重连死循环
    while True:
        try:
            logger.info(f"[连接尝试] 正在连接 MC 插件服务器...")
            # 设置较大的 max_size 以支持接收大数据包 (如地图数据)
            async with connect(config.McPlugin_WS_URI,
                               additional_headers=extra_headers,
                               ping_interval=20,
                               ping_timeout=20,
                               max_size=2**24) as websocket:

                logger.info(f"[连接成功] 已连接到 MC 插件! 双向通道建立。")
                _active_mc_ws = websocket

                # --- 消息监听循环 ---
                async for message in websocket:
                    try:
                        data = json.loads(message)

                        # 检查是否是 API 响应 (带有 echo 字段)
                        if config.MCPLUGIN_ENABLE_ECHO:
                            echo_id = data.get('echo')
                            if echo_id:
                                # 处理 API 响应
                                future = _pending_api_requests.get(echo_id)
                                if future and not future.done():
                                    future.set_result(data)
                                    logger.debug(f"[API响应] 收到 MC 响应 echo: {echo_id}")
                                continue

                        # 处理普通通知消息 (调用业务回调)
                        if _mcplugin_message_handler:
                            # 【重要】保护性调用业务回调
                            try:
                                await _mcplugin_message_handler(data)
                            except Exception as business_err:
                                logger.error(f"[业务回调异常] 处理 MC 插件消息时出错: {business_err}", exc_info=True)
                        elif config.DEBUG_MODE:
                            logger.debug("[接收] 收到 MC 消息但未设置回调，已丢弃。")

                    except json.JSONDecodeError:
                        logger.warning(f"[接收] 收到 MC 插件非法 JSON 数据，长度: {len(message)}")
                # -------------------

            logger.info("[连接断开] 与 MC 插件的连接已正常关闭。")

        # --- 异常处理与重连机制 ---
        except (ConnectionRefusedError, OSError):
            logger.warning(f"[连接失败] 无法连接到 MC 插件 ({config.McPlugin_WS_URI})。请检查服务器是否开启。")
        except ConnectionClosed as e:
            logger.warning(f"[连接中断] 与 MC 插件的连接意外断开，代码: {e.code}, 原因: {e.reason}")
        except Exception as e:
            logger.error(f"[连接异常] MC 插件客户端发生意外错误: {e}", exc_info=True)
        finally:
            # 清理全局连接对象
            if _active_mc_ws is not None:
                logger.debug("[连接清理] 清除活跃连接对象标记。")
                _active_mc_ws = None

            logger.info(f"[重连] {config.McPlugin_RECONNECT_INTERVAL} 秒后尝试重连 MC 插件...")
            await asyncio.sleep(config.McPlugin_RECONNECT_INTERVAL)


if __name__ == "__main__":
    # (测试部分省略)
    pass