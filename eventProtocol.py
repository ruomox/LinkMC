# eventProtocol.py
from typing import Dict, Any

# ============================================================
# MC Plugin (QueQiao) 全字段事件模型定义
# ============================================================
# 说明：
# - 所有事件共享同一套字段
# - 任意字段在某事件 / 某插件中缺失 → 值为 None
# - mapper / 业务层只允许使用这些字段名
# ============================================================

MC_EVENT_FIELDS = {
    # ---------- 事件标识 ----------
    "event": None,                 # 建议使用 sub_type
    "timestamp": None,
    "post_type": None,
    "event_name": None,
    "sub_type": None,

    # ---------- 服务端信息 ----------
    "server_name": None,
    "server_version": None,
    "server_type": None,

    # ---------- 消息相关 ----------
    "message_id": None,
    "raw_message": None,
    "message": None,               # chat
    "command": None,               # command

    # ---------- 玩家基础信息 ----------
    "player_nickname": None,
    "player_uuid": None,
    "player_is_op": None,
    "player_address": None,

    # ---------- 玩家状态 ----------
    "player_health": None,
    "player_max_health": None,
    "player_experience_level": None,
    "player_experience_progress": None,
    "player_total_experience": None,
    "player_walk_speed": None,

    # ---------- 玩家位置 ----------
    "player_x": None,
    "player_y": None,
    "player_z": None,

    # ---------- 死亡事件 ----------
    "death_key": None,
    "death_args": None,
    "death_text": None,

    # ---------- 成就事件 ----------
    "achievement_key": None,
    "achievement_text": None,
    "achievement_display_title": None,
    "achievement_display_description": None,
    "achievement_display_frame": None,
}

# ============================================================
# QueQiao V2 事件字段映射表
# ============================================================
# key = sub_type
# value = 字段名 → 原始 JSON 路径
# ============================================================

MC_EVENT_FIELD_MAP: Dict[str, Dict[str, tuple]] = {

    "player_chat": {
        "event": ("sub_type",),
        "timestamp": ("timestamp",),
        "post_type": ("post_type",),
        "event_name": ("event_name",),
        "sub_type": ("sub_type",),

        "server_name": ("server_name",),
        "server_version": ("server_version",),
        "server_type": ("server_type",),

        "message_id": ("message_id",),
        "raw_message": ("raw_message",),
        "message": ("message",),

        "player_nickname": ("player", "nickname"),
        "player_uuid": ("player", "uuid"),
        "player_is_op": ("player", "is_op"),
        "player_address": ("player", "address"),

        "player_health": ("player", "health"),
        "player_max_health": ("player", "max_health"),
        "player_experience_level": ("player", "experience_level"),
        "player_experience_progress": ("player", "experience_progress"),
        "player_total_experience": ("player", "total_experience"),
        "player_walk_speed": ("player", "walk_speed"),

        "player_x": ("player", "x"),
        "player_y": ("player", "y"),
        "player_z": ("player", "z"),
    },

    "player_command": {
        "event": ("sub_type",),
        "timestamp": ("timestamp",),
        "post_type": ("post_type",),
        "event_name": ("event_name",),
        "sub_type": ("sub_type",),

        "server_name": ("server_name",),
        "server_version": ("server_version",),
        "server_type": ("server_type",),

        "message_id": ("message_id",),
        "raw_message": ("raw_message",),
        "command": ("command",),

        "player_nickname": ("player", "nickname"),
        "player_uuid": ("player", "uuid"),
        "player_is_op": ("player", "is_op"),
    },

    "player_death": {
        "event": ("sub_type",),
        "timestamp": ("timestamp",),
        "post_type": ("post_type",),
        "event_name": ("event_name",),
        "sub_type": ("sub_type",),

        "server_name": ("server_name",),

        "player_nickname": ("player", "nickname"),

        "death_key": ("death", "key"),
        "death_args": ("death", "args"),
        "death_text": ("death", "text"),
    },

    "player_achievement": {
        "event": ("sub_type",),
        "timestamp": ("timestamp",),
        "post_type": ("post_type",),
        "event_name": ("event_name",),
        "sub_type": ("sub_type",),

        "server_name": ("server_name",),

        "player_nickname": ("player", "nickname"),

        "achievement_key": ("achievement", "key"),
        "achievement_text": ("achievement", "text"),

        "achievement_display_title": ("achievement", "display", "title"),
        "achievement_display_description": ("achievement", "display", "description"),
        "achievement_display_frame": ("achievement", "display", "frame"),
    },
    "player_join": {
        "event": ("sub_type",),
        "timestamp": ("timestamp",),
        "post_type": ("post_type",),
        "event_name": ("event_name",),
        "sub_type": ("sub_type",),

        "server_name": ("server_name",),
        "server_version": ("server_version",),
        "server_type": ("server_type",),

        # Player
        "player_nickname": ("player", "nickname"),
        "player_uuid": ("player", "uuid"),
        "player_is_op": ("player", "is_op"),
        "player_address": ("player", "address"),

        "player_health": ("player", "health"),
        "player_max_health": ("player", "max_health"),
        "player_experience_level": ("player", "experience_level"),
        "player_experience_progress": ("player", "experience_progress"),
        "player_total_experience": ("player", "total_experience"),
        "player_walk_speed": ("player", "walk_speed"),

        "player_x": ("player", "x"),
        "player_y": ("player", "y"),
        "player_z": ("player", "z"),
    },
    "player_quit": {
        "event": ("sub_type",),
        "timestamp": ("timestamp",),
        "post_type": ("post_type",),
        "event_name": ("event_name",),
        "sub_type": ("sub_type",),

        "server_name": ("server_name",),
        "server_version": ("server_version",),
        "server_type": ("server_type",),

        # Player（退出事件通常还能拿到完整 player）
        "player_nickname": ("player", "nickname"),
        "player_uuid": ("player", "uuid"),
        "player_is_op": ("player", "is_op"),
        "player_address": ("player", "address"),

        "player_health": ("player", "health"),
        "player_max_health": ("player", "max_health"),
        "player_experience_level": ("player", "experience_level"),
        "player_experience_progress": ("player", "experience_progress"),
        "player_total_experience": ("player", "total_experience"),
        "player_walk_speed": ("player", "walk_speed"),

        "player_x": ("player", "x"),
        "player_y": ("player", "y"),
        "player_z": ("player", "z"),
    },
}

def build_event(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    根据协议字段全集 + 映射表，构建标准事件对象
    - 不猜字段
    - 不裁剪
    - 不修改语义
    """
    sub_type = raw.get("sub_type")
    field_map = MC_EVENT_FIELD_MAP.get(sub_type)

    # 未支持事件：仍返回全字段空对象
    event = dict(MC_EVENT_FIELDS)

    if not field_map:
        return event

    for field_name, path in field_map.items():
        value = raw
        for key in path:
            if not isinstance(value, dict):
                value = None
                break
            value = value.get(key)
        event[field_name] = value

    return event


# ============================================================
# MC Plugin (QueQiao) 原始事件文档
# ============================================================
# 事件:
# 当前 V2 事件协议 适用于 v0.3.0 及以上版本的鹊桥服务端插件/Mod。
# 概述:
# 事件将更多地偏向于与玩家、互通有关的事件，而非服务端所有实体的事件
# 如果您想对更多事件进行操作，应该去编写对应服务端的 插件/MOD
# 本页面是所有的基本事件类型，各服务端的事件类型均继承基本事件且有不同程度扩展
# 由于服务端版本不同，同服务端的不同版本之间也会大同小异
# 事件会通过 Websocket 以 Json 的形式分发
# 字段相关:
# 已尽力为每个字段填充内容。但在事件统一、多服务端多版本的情况下仍可能存在部分字段为空的情况
# 缺失值的字段具体如 PlayerAchievementEvent 中 achievement 内的 description，亦或者是 PlayerDeathEvent 中 death 内的部分字段。
# 如遇到字段缺失情况，可提交 Issue 获取帮助。欢迎有能力者在提交 Issue 的同时，提供服务端对应源码的实现示例等
#
# PlayerChatEvent:
# 字段名	            数据类型	 可能的值	       说明
# timestamp	        int	        -	           事件时间戳
# post_type	        str	     message	       事件类型
# event_name	    str	     PlayerChatEvent   事件名
# server_name	    str	        -	           服务器名称
# server_version	str	        -	           服务器版本
# server_type	    str	        -	           服务器类型
# sub_type	        str	     player_chat	   事件子类型
# message_id	    str	        -	           消息 ID
# raw_message	    str	        -	           原始消息内容
# player	        Player	    -	           玩家对象
# message	        str	        -	           消息对象
# 提示: 可通过以下方式拼接成聊天消息
# chat_message = f"[{event.server_name}] {event.player.nickname}：{event.message}"
# [Server] 玩家A：你好！
# 服务端支持情况:
# raw_message 字段
# 在 vanilla (原版) 与 Spigot 中，均与 message 字段相同。
# 在其他服务端中，为玩家聊天消息的 Json 文本组件格式字符串，但如果消息没有使用任何格式化，则与 message 字段相同。
# 例如：玩家发送消息 Hello，则 raw_message 字段为 Hello；
# 玩家发送消息 &dHello，则 raw_message 字段可能为 {"text":"Hello","color":"light_purple"}（暂未测试）。
#
# PlayerCommandEvent:
# 字段名	            数据类型	 可能的值	        说明
# timestamp	        int	        -	            事件时间戳
# post_type	        str	     message	        事件类型
# event_name	    str	     PlayerCommandEvent	事件名
# server_name	    str	        -	            服务器名称
# server_version	str	        -	            服务器版本
# server_type	    str	        -	            服务器类型
# sub_type	        str	     player_command	    事件子类型
# message_id	    str	        -	            消息 ID
# raw_message	    str	        -	            原始消息内容
# player	        Player	    -	            玩家对象
# command	        str	        -	            玩家输入的命令内容
# 提示: 可以对命令消息进行监听和处理，搭配 Rcon 实现模组服中无权限管理插件的简单TP命令功能。
# 服务端支持情况:
# 不支持 原版端、Velocity
# raw_message 字段一般情况与 command 字段相同，如有特殊情况，欢迎 PR 标记补充。
#
# PlayerJoinEvent:
# 字段名	            数据类型	可能的值	          说明
# timestamp	        int	       -	          事件时间戳
# post_type	        str	    notice	          通知事件类型
# event_name	    str	    PlayerJoinEvent	  事件名
# server_name	    str	       -	          服务器名称
# server_version	str	       -	          服务器版本
# server_type	    str	       -	          服务器类型
# sub_type	        str	    player_join	      事件子类型
# player	        Player	   -	          玩家对象
# 提示:
# 可通过以下方式拼接成玩家加入消息
# join_message = f"[{event.server_name}] {event.player.nickname} 加入了游戏"
# [Server] 玩家A 加入了游戏
#
# PlayerQuitEvent:
# 同 PlayerJoinEvent
# 提示: 可通过以下方式拼接成玩家退出消息
# quit_message = f"[{event.server_name}] {event.player.nickname} 离开了游戏"
# [Server] 玩家A 离开了游戏
#
# PlayerDeathEvent:
# 字段名	            数据类型	可能的值	          说明
# timestamp	        int	       -	          事件时间戳
# post_type	        str	    notice	          通知事件类型
# event_name	    str	    PlayerDeathEvent  事件名
# server_name	    str	       -	          服务器名称
# server_version	str	       -	          服务器版本
# server_type	    str	       -	          服务器类型
# sub_type	        str	    player_death	  事件子类型
# player	        Player	   -	          玩家对象
# death	            Death	   -	          死亡详情
# Death:
# 字段名	            数据类型	可能的值	          说明
# key	            str	       -	          用于翻译的 Key
# args	            list[str]  -	          翻译参数列表
# text	            str	       -	          死亡消息内容
# 提示: 可通过以下方式拼接成玩家死亡消息
# death_message = f"[{event.server_name}] {event.death.text}"
# [Server] 玩家A was slain by Zombie
# 服务端支持情况
# 不支持 原版端、Velocity
#
# PlayerAchievementEvent:
# 字段名	            数据类型	 可能的值	            说明
# timestamp	        int	        -	                事件时间戳
# post_type	        str	     notice	                通知事件类型
# event_name	    str	     PlayerAchievementEvent	事件名
# server_name	    str	        -	                服务器名称
# server_version	str	        -	                服务器版本
# server_type	    str	        -	                服务器类型
# sub_type	        str	     player_achievement	    事件子类型
# player	        Player	    -	                玩家对象
# achievement	    Achievement -	                成就详情
# Achievement:
# 字段名	            数据类型	 可能的值	            说明
# key	            str	        -	                成就资源文件中的 Key
# display	        Display	    -	                成就显示信息
# text	            str	        -	                成就事件的文本
# 提示: 可通过以下方式拼接成就获得消息
# achievement_message = f"[{event.server_name}] {event.achievement.text}"
# [Server] 玩家A has earned the achievement [Getting Wood]
# Display:
# 字段名	            数据类型	 可能的值	            说明
# title	            str	        -	                标题的 Key
# description	    str	        -	                描述的 Key
# frame	            str	     task/goal/challenge    显示框架类型
# 服务端支持情况
# 不支持 原版端、Velocity
# 字段缺失统计:
# Spigot 仅包含 key
# Forge 1.7.10：缺失 achievement.display.description
#
# Player:
# 字段名	                数据类型	可能的值	说明
# nickname	            str	       -	玩家昵称
# uuid	                UUID	   -	玩家 UUID
# is_op	                bool	   -	玩家是否为管理员
# address	            str	       -	玩家 IP 地址
# health	            float	   -	当前生命值
# max_health	        float	   - 	最大生命值
# experience_level	    int	       -	玩家经验等级
# experience_progress	float	   -	当前经验进度（0.0–1.0）
# total_experience	    int	       -	玩家总经验值
# walk_speed	        float	   -	行走速度
# x	                    float	   -	坐标 X
# y	                    float	   -	坐标 Y
# z	                    float	   -	坐标 Z
# 字段缺失统计:
# 原版端 仅支持 nickname
# Spigot：不支持 max_health
# Paper：不支持 max_health
# Folia：
# 不支持 max_health
# 可能缺失 address
# Velocity 仅支持 nickname、uuid、is_op
# Forge
# 1.7.10：缺少 address
