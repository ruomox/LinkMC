# messageMapper.py
import logging
import config

# 仅导入【公共发送接口】，不触碰任何私有实现
from server4NapCat import send_to_napcat_async_notification
from client4McPlugin import send_to_mc_async_notification
# 导入事件标准化工具
from config import build_event

logger = logging.getLogger("MessageMapper")

# ============================================================
# 工具函数 (Helper)
# ============================================================
async def _send_qq_text_msg(message: str):
    """
    [助手] 发送纯文本消息到目标 QQ 群
    """
    if not message:
        return

    # 构建 OneBot 标准的消息发送 Payload
    onebot_payload = {
        "action": "send_group_msg",
        "params": {
            "group_id": config.TARGET_QQ_GROUP_ID,
            "message": message,
        },
    }
    # 调用底层接口发送
    success = await send_to_napcat_async_notification(onebot_payload)
    if not success:
        logger.warning(f"[发送失败] 尝试发送到QQ群失败: {message[:30]}...")


# ============================================================
# QQ -> MC 方向：语义 → MC 协议映射
# ============================================================
# ... (map_qq_to_mc 函数与你之前提供的一模一样，请保持原样) ...
# 为了篇幅，这里省略了 map_qq_to_mc 的代码，实际文件中需要包含它
async def map_qq_to_mc(data: dict):
    # --------------------------------------------------------
    # 1. 语义提取（只关心我们需要的事件）
    # --------------------------------------------------------
    if data.get("post_type") != "message":
        return
    if data.get("message_type") != "group":
        return

    group_id = data.get("group_id")
    if data.get("group_id") != config.TARGET_QQ_GROUP_ID:
        return

    # 读取群名（NapCat 已提供）
    group_name = (data.get("group_name") or "").strip()

    # 兜底：极端情况下没有群名
    if not group_name:
        group_name = f"群{group_id}"

    sender_info = data.get("sender", {})
    nickname = (
            sender_info.get("card")
            or sender_info.get("nickname")
            or "未知QQ用户"
    )
    raw_message = data.get("raw_message", "")

    logger.info(
        f"[QQ -> MC] 群消息: [{group_name}] [{nickname}] {raw_message}"
    )

    # --------------------------------------------------------
    # 2. 业务加工（文本处理、过滤、替换等）
    #    ⚠️ 这是“唯一允许随意加逻辑”的地方
    # --------------------------------------------------------

    processed_message = raw_message
    # 2.1 过滤 QQ 富文本（默认拒绝）
    # CQ 码（表情 / 图片 / 语音 / 链接等）一律拦截
    if "[CQ:" in processed_message:
        logger.debug("[QQ -> MC] 检测到 CQ 富文本，已拦截")
        return
    # 2.2 过滤链接
    if processed_message.startswith("http://") or processed_message.startswith("https://"):
        logger.debug("[QQ -> MC] 检测到链接，已拦截")
        return
    # 2.3 只允许“纯文本”
    processed_message = processed_message.strip()
    if not processed_message:
        return
    # 示例：
    # processed_message = processed_message.replace("我是笨蛋", "我是小可爱")

    # --------------------------------------------------------
    # 3. 协议映射（核心）
    #    不关心 JSON 结构，只声明“我要干什么”
    # --------------------------------------------------------
    success = await send_to_mc_async_notification(
        kind="mc.broadcast",     # ← 与 MCPLUGIN_PROTOCOL 中定义的 key 对齐
        group=group_name,
        sender=nickname,
        content=processed_message,
    )

    if not success:
        logger.warning(
            "[QQ -> MC] 转发失败：底层发送返回 False（可能连接断开）"
        )


# ============================================================
# MC -> QQ 方向：MC 事件 → QQ 消息
# ============================================================

async def map_mc_to_qq(raw: dict):
    """
    【业务层】
    处理来自 MC 插件的原始事件，标准化后分发处理。
    """

    # --------------------------------------------------------
    # 0. 构建标准事件对象（防腐层接入）
    # --------------------------------------------------------
    # 使用 eventProtocol.py 将原始 JSON 转换为标准化的全字段字典
    event = build_event(raw)
    # 获取事件标识名，如 "PlayerChatEvent"
    event_name = event.get("event_name")

    # 提取通用基础信息
    server_name = event.get("server_name") or "MC"
    # 大部分事件都与特定玩家有关，尝试提取昵称
    player_nickname = event.get("player_nickname") or "未知玩家"

    # 用于存储最终要发送的文本消息，为空则不发送
    final_message = ""
    # 日志前缀，方便排查问题
    log_prefix = f"[MC -> QQ] [{server_name}]"

    # --------------------------------------------------------
    # 1. 事件分发与处理 (Dispatcher)
    # --------------------------------------------------------

    # --- 玩家聊天 (PlayerChatEvent) ---
    if event_name == "PlayerChatEvent":
        # 检查配置开关
        if not config.ENABLE_MC_CHAT_FORWARD:
            return

        # 从标准字段中获取消息内容
        chat_message = event.get("message")
        if chat_message:
            logger.info(f"{log_prefix} <{player_nickname}> 聊天: {chat_message}")
            # 格式化显示文本
            final_message = f"[{server_name}] <{player_nickname}> {chat_message}"


    # --- 玩家加入 (PlayerJoinEvent) ---
    elif event_name == "PlayerJoinEvent":
        if not config.ENABLE_MC_JOIN_NOTICE:
            return

        logger.info(f"{log_prefix} 玩家加入: {player_nickname}")
        final_message = f"[{server_name}] 🟢 欢迎 {player_nickname} 加入游戏!"


    # --- 玩家退出 (PlayerQuitEvent) ---
    elif event_name == "PlayerQuitEvent":
        if not config.ENABLE_MC_QUIT_NOTICE:
            return

        logger.info(f"{log_prefix} 玩家退出: {player_nickname}")
        final_message = f"[{server_name}] 🔴 {player_nickname} 离开了游戏。"


    # --- 玩家死亡 (PlayerDeathEvent) ---
    elif event_name == "PlayerDeathEvent":
        if not config.ENABLE_MC_DEATH_NOTICE:
            return

        # death_text 通常是由服务端翻译好的完整句子，如 "Player was slain by Zombie"
        death_msg = event.get("death_text") or f"{player_nickname} 不幸去世了"

        logger.info(f"{log_prefix} 玩家死亡: {death_msg}")
        final_message = f"[{server_name}] ☠️ {death_msg}"


    # --- 玩家获得成就 (PlayerAchievementEvent) ---
    elif event_name == "PlayerAchievementEvent":
        if not config.ENABLE_MC_ACHIEVEMENT_NOTICE:
            return

        # 获取成就文本
        ach_text = event.get("achievement_text")
        # 也可以获取更详细的显示标题
        # ach_title = event.get("achievement_display_title")

        if ach_text:
            logger.info(f"{log_prefix} 玩家成就: {player_nickname} -> [{ach_text}]")
            final_message = f"[{server_name}] 🎉 恭喜 {player_nickname} 达成了成就 [{ach_text}]!"


    # --- 玩家执行命令 (PlayerCommandEvent) ---
    elif event_name == "PlayerCommandEvent":
        if not config.ENABLE_MC_COMMAND_FORWARD:
            return

        command_str = event.get("command")
        # 为了防止刷屏，建议只在 info 记录简要信息
        logger.info(f"{log_prefix} 玩家命令: {player_nickname} -> /{command_str}")
        # 注意：转发命令可能会泄露敏感信息，请谨慎开启
        final_message = f"[{server_name}] ℹ️ {player_nickname} 执行了命令: /{command_str}"

    # --------------------------------------------------------
    # 2. 统一发送
    # --------------------------------------------------------
    if final_message:
        # 调用辅助函数发送到 QQ 群
        await _send_qq_text_msg(final_message)
