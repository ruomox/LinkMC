# ============================================
# 项目配置文件
# ============================================

# --- 转发配置 ---
# QQ ↔ MC 互通目标群号
TARGET_QQ_GROUP_ID = 00000000
# --- MC 事件转发开关 ---
# 根据需求调整默认值
ENABLE_MC_CHAT_FORWARD = True         # 玩家聊天
ENABLE_MC_COMMAND_FORWARD = True      # 玩家执行命令 (默认关闭，防止刷屏)
ENABLE_MC_JOIN_NOTICE = True          # 玩家加入游戏
ENABLE_MC_QUIT_NOTICE = True          # 玩家离开游戏
ENABLE_MC_DEATH_NOTICE = True         # 玩家死亡
ENABLE_MC_ACHIEVEMENT_NOTICE = True   # 玩家获得成就

# --- NapCat 连接配置 (Python作为服务端等待连接) ---
# 监听地址，0.0.0.0 表示允许所有 IP 连接
NAPCAT_WS_HOST = "0.0.0.0"
# 监听端口，需与 NapCat WebUI 配置一致
NAPCAT_WS_PORT = 6100
# 鉴权 Token，需与 NapCat WebUI 配置一致
NAPCAT_WS_TOKEN = "00000000"
# Server 是否支持 echo-response API
NAPCAT_ENABLE_ECHO = True

# --- McPlugin 连接配置 (Python作为客户端主动去连) ---
# McPlugin 插件 WebSocket 服务的地址 (通常是本机)
# 注意：最新的 websockets 库推荐使用 ws:// 前缀的完整 URI
McPlugin_SELF_NAME = "前缀名"
McPlugin_WS_URI = "ws://127.0.0.1:6101"
# 鉴权 Token，需与 McPlugin config.yml 配置一致
McPlugin_WS_TOKEN = "00000000"
# 断线重连间隔 (秒)
McPlugin_RECONNECT_INTERVAL = 5
# 是否启用 echo-response 请求/响应机制
# False = 仅作为事件流（推荐默认）
# True  = 启用 call_mc_plugin_api
MCPLUGIN_ENABLE_ECHO = False
# === MC Plugin 协议定义 ===
from messageProtocol import MCPLUGIN_PROTOCOL
from eventProtocol import build_event


# --- 其他配置 ---
# 是否开启调试模式 (打印更详细的日志)
DEBUG_MODE = False