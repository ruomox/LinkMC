# main.py
import asyncio
import logging

import config
import server4NapCat
import client4McPlugin
import messageMapper

logging.basicConfig(
    level=logging.DEBUG if config.DEBUG_MODE else logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("MainBridge")


# ==========================================
# 主程序入口
# ==========================================

async def main():
    logger.info("=" * 40)
    logger.info("   Python 双向中枢核心 (Modular Refactored) 正在启动...")
    logger.info("=" * 40)

    # --- 注册业务逻辑回调 ---
    logger.info("-> 正在注册业务逻辑处理函数 (连接 messageMapper)...")

    # QQ -> MC
    server4NapCat.register_napcat_message_handler(
        messageMapper.map_qq_to_mc
    )

    # MC -> QQ
    client4McPlugin.register_mcplugin_message_handler(
        messageMapper.map_mc_to_qq
    )

    logger.info("-> 业务回调注册完毕，中枢神经已连接。")

    tasks = []

    logger.info("-> 正在创建 NapCat 服务端任务 (WebSocket Server)...")
    tasks.append(asyncio.create_task(server4NapCat.start_server()))

    logger.info("-> 正在创建 McPlugin 客户端任务 (WebSocket Client)...")
    tasks.append(asyncio.create_task(client4McPlugin.run_client_task()))

    logger.info("✅ 所有底层子模块启动完毕，双向转发中枢开始运行。")

    await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 40)
        logger.info("🔻 收到终止信号 (Ctrl+C)，中枢核心正在安全关闭...")
        logger.info("=" * 40)