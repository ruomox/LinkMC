import asyncio
import json
import logging
import uuid
from typing import Callable, Awaitable, Optional, Set, Dict, Any

# 引入最新的 websockets 服务端模块
from websockets.asyncio.server import serve, ServerConnection
from websockets.exceptions import ConnectionClosedError

import config

# 配置日志
logger = logging.getLogger("NapCatServer")

# --- 类型定义 ---
# 回调函数类型：接收 dict，返回 Awaitable[None]
MessageHandlerType = Callable[[Dict[str, Any]], Awaitable[None]]

# --- 全局状态管理 ---
# NapCat 消息接收回调（由外部注入）
_napcat_message_handler: Optional[MessageHandlerType] = None

# 保存所有活跃连接的集合
_active_connections: Set[ServerConnection] = set()
# 用于轮询选择连接的迭代器
_connection_iterator = None

# 挂起的 API 请求字典 {echo_uuid: asyncio.Future}
# 用于存储等待响应的 Future 对象
_pending_api_requests: Dict[str, asyncio.Future] = {}


# ==========================================
# 对外公共接口 (Public API)
# ==========================================

def register_napcat_message_handler(handler: MessageHandlerType):
    """
    [接口] 注册 NapCat 消息处理函数 (业务逻辑入口)
    """
    global _napcat_message_handler
    _napcat_message_handler = handler
    logger.info("已注册 NapCat 消息处理回调函数。")


async def call_napcat_api(action: str, params: Optional[Dict] = None, timeout: float = 10.0) -> Dict[str, Any]:
    """
    [接口] 调用 NapCat API 并异步等待响应结果 (核心功能)

    :param action: API 动作名称，如 'send_group_msg'
    :param params: API 参数字典
    :param timeout: 等待响应的超时时间(秒)
    :return: API 响应结果字典 (包含 status, retcode, data 等)
    :raises asyncio.TimeoutError: 请求超时
    :raises ConnectionError: 没有可用的连接
    :raises Exception: 其他发送错误
    """
    # 1. 生成唯一的请求追踪 ID (echo)
    request_uuid = str(uuid.uuid4())

    # 2. 构建请求数据包
    payload = {
        "action": action,
        "params": params or {},
        "echo": request_uuid  # 关键：携带 echo 字段
    }

    # 3. 创建一个 Future 对象，用于接收未来的结果
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    _pending_api_requests[request_uuid] = future

    try:
        # 4. 发送请求 (复用底层的发送逻辑)
        # 如果发送失败，send_to_napcat 会抛出异常，这里捕获并清理 future
        await _send_to_napcat_impl(payload)
        logger.debug(f"[API调用] 已发送请求: {action}, echo: {request_uuid}")

        # 5. 等待 Future 完成 (设置超时)
        # 当接收循环收到带有相同 echo 的响应时，会设置这个 future 的结果
        response = await asyncio.wait_for(future, timeout)
        return response

    except asyncio.TimeoutError:
        logger.error(f"[API调用失败] 请求超时 ({timeout}s): {action}, echo: {request_uuid}")
        raise
    except Exception as e:
        logger.error(f"[API调用失败] 发送请求时出错: {e}, echo: {request_uuid}")
        raise ConnectionError(f"Failed to send API request: {e}") from e
    finally:
        # 6. 清理：无论成功还是失败，都要移除挂起的请求，防止内存泄漏
        _pending_api_requests.pop(request_uuid, None)


async def send_to_napcat_async_notification(data_dict: dict) -> bool:
    """
    [接口] 发送异步通知数据到 NapCat (不等待响应)
    适用于无需回复的场景。
    """
    # 确保不携带 echo，避免污染 API 请求池
    if 'echo' in data_dict:
        del data_dict['echo']

    try:
        await _send_to_napcat_impl(data_dict)
        return True
    except Exception:
        # _send_to_napcat_impl 已经记录了错误日志
        return False

# ==========================================
# 内部实现细节 (Internal Implementation)
# ==========================================

async def _send_to_napcat_impl(data_dict: dict):
    """
    [内部] 底层发送实现，负责选择连接并执行发送操作
    """
    global _connection_iterator

    if not _active_connections:
        raise ConnectionError("No active NapCat connections available.")

    # 使用轮询 (Round-Robin) 策略选择一个连接
    # 简单的实现：如果迭代器耗尽或失效，重新创建
    if _connection_iterator is None:
        _connection_iterator = iter(_active_connections)

    try:
        target_ws = next(_connection_iterator)
    except StopIteration:
        # 迭代器用完了，重置并再取一次
        _connection_iterator = iter(_active_connections)
        try:
            target_ws = next(_connection_iterator)
        except StopIteration:
            # 极端的并发情况：刚检查有连接，取的时候没了
            raise ConnectionError("Connection pool became empty during selection.")

    # 执行发送
    try:
        json_str = json.dumps(data_dict, ensure_ascii=False)
        await target_ws.send(json_str)
        if config.DEBUG_MODE and 'echo' not in data_dict:
            # 仅在不是 API 请求时打印详细发送日志，避免刷屏
            logger.debug(f"[中枢 -> NapCat(通知)] 已发送: {json_str[:150]}...")
    except Exception as e:
        logger.error(f"[底层发送失败] 目标: {target_ws.remote_address}, 错误: {e}")
        # 发送失败可能是连接断了，但让 handle_connection 的 finally 块去处理移除逻辑
        # 这里只抛出异常通知上层
        raise


async def _handle_api_response(data: Dict[str, Any], echo_id: str):
    """
    [内部] 处理 API 响应结果
    """
    future = _pending_api_requests.get(echo_id)
    if future and not future.done():
        # 找到对应的 Future，设置结果，唤醒等待者
        future.set_result(data)
        logger.debug(f"[API响应] 已处理 echo: {echo_id}, 状态: {data.get('status')}")
    else:
        logger.warning(f"[API响应过期] 收到了一个未知的或已超时的响应, echo: {echo_id}")


async def handle_napcat_connection(websocket: ServerConnection):
    """
    [内部] WebSocket 连接处理器 (每个连接一个协程)
    """
    # 1. 鉴权
    auth_header = websocket.request.headers.get("Authorization")
    if auth_header != f"Bearer {config.NAPCAT_WS_TOKEN}":
        logger.warning(f"[安全] 拒绝未授权连接: {websocket.remote_address}")
        await websocket.close(code=4001, reason="Unauthorized")
        return

    logger.info(f"[连接管理] NapCat 已连接: {websocket.remote_address}")
    _active_connections.add(websocket)
    # 重置迭代器以纳入新连接
    global _connection_iterator
    _connection_iterator = None

    try:
        # 2. 消息接收循环
        async for message in websocket:
            try:
                data = json.loads(message)

                # 检查是否是 API 响应 (带有 echo 字段)
                echo_id = data.get('echo')
                if echo_id:
                    if not config.NAPCAT_ENABLE_ECHO:
                        logger.warning(
                            f"[API] Client sent echo={echo_id}, but echo-response is disabled"
                        )
                        # 明确拒绝，而不是静默丢弃
                        await websocket.send(json.dumps({
                            "status": "failed",
                            "retcode": 400,
                            "message": "echo-response disabled on server"
                        }))
                        continue
                    # ---> 进入 API 响应处理流程
                    await _handle_api_response(data, echo_id)
                    continue

                # 过滤心跳包 (Meta Event)
                if data.get('post_type') == 'meta_event':
                    continue

                # ---> 进入普通事件处理流程 (调用业务回调)
                if _napcat_message_handler:
                    # 【重要】使用 try-except 包裹业务逻辑，防止回调出错搞崩底层连接
                    try:
                        await _napcat_message_handler(data)
                    except Exception as business_err:
                        logger.error(f"[业务回调异常] 处理 NapCat 事件时出错: {business_err}", exc_info=True)
                elif config.DEBUG_MODE:
                    logger.debug("[接收] 收到事件但未设置回调，已丢弃。")

            except json.JSONDecodeError:
                logger.warning(f"[接收] 收到非法 JSON 数据，长度: {len(message)}")

    except ConnectionClosedError as e:
        logger.info(f"[连接断开] NapCat 连接关闭: {websocket.remote_address}, 代码: {e.code}, 原因: {e.reason}")
    except Exception as e:
        logger.error(f"[连接异常] 处理连接时发生意外错误: {websocket.remote_address}, {e}", exc_info=True)
    finally:
        # 3. 清理工作
        _active_connections.discard(websocket)
        _connection_iterator = None # 重置迭代器
        logger.info(f"[连接清理] 连接已移除: {websocket.remote_address}. 剩余活跃连接: {len(_active_connections)}")


async def start_server():
    """
    [内部] 启动监听服务的主入口
    """
    logger.info(f"[服务启动] 正在初始化 NapCat 监听: ws://{config.NAPCAT_WS_HOST}:{config.NAPCAT_WS_PORT}")
    # 设置较高的 max_size 防止处理大图片数据包时报错
    async with serve(handle_napcat_connection, config.NAPCAT_WS_HOST, config.NAPCAT_WS_PORT, max_size=2**24):
        logger.info("[服务已就绪] NapCat WebSocket 服务器开始监听。")
        # 创建一个永远处于 pending 状态的 Future，让服务一直运行下去
        await asyncio.get_running_loop().create_future()


# 单元测试入口
if __name__ == "__main__":
    # 简单的测试存根
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] %(levelname)s: %(message)s')

    # 注册一个测试回调
    async def test_handler(data):
        print(f">> [测试回调] 收到数据: {data.get('post_type')}")

    register_napcat_message_handler(test_handler)

    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\n[测试结束] 服务器停止。")