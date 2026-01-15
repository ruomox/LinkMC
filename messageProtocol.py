# ============================================================
# MC Plugin (QueQiao) Protocol Definitions
# ============================================================

# 说明：
# - key (kind)：业务语义名称（业务层 / client 使用）
# - api        ：QueQiao 实际 API 名称
# - data       ：发送给 QueQiao 的 JSON data 模板
# - 所有字符串都会通过 str.format(**kwargs) 填充
# ============================================================

MCPLUGIN_PROTOCOL = {
    # --------------------------------------------------------
    # 广播消息接口（broadcast）
    # --------------------------------------------------------
    "mc.broadcast": {
        "api": "broadcast",
        "data": {
            "message": [
                { "text": "[{group}]", "color": "aqua" },
                { "text": " {sender}", "color": "green" },
                { "text": " :", "color": "white" },
                { "text": " {content}", "color": "white" }
            ]
        }
    },
    # 业务层调用示例（异步通知，不等待返回）:
    # await send_to_mc_async_notification(
    #     "mc.broadcast",
    #     group="群名1",
    #     sender="QQ用户",
    #     content="聊天内容"
    # )

    # --------------------------------------------------------
    # 私聊消息接口（send_private_msg）
    # --------------------------------------------------------
    "mc.private_message": {
        "api": "send_private_msg",
        "data": {
            # uuid 与 nickname 至少提供一个
            "uuid": "{uuid}",
            "nickname": "{nickname}",
            "message": [
                { "text": "[私聊]", "color": "aqua" },
                { "text": " {sender}", "color": "green" },
                { "text": "说:", "color": "white" },
                { "text": " {content}", "color": "white" }
            ]
        }
    },
    # 业务层调用示例（异步通知）:
    # await send_to_mc_async_notification(
    #     "mc.private_message",
    #     uuid="",                    # 可为空
    #     nickname="17TheWord",
    #     sender="QQ用户",
    #     content="你好"
    # )

    # --------------------------------------------------------
    # 标题推送接口（send_title）
    # --------------------------------------------------------
    "mc.title": {
        "api": "send_title",
        "data": {
            "title": {
                "text": "{title}",
                "color": "aqua"
            },
            "subtitle": {
                "text": "{subtitle}"
            },
            "fade_in": "{fade_in}",
            "stay": "{stay}",
            "fade_out": "{fade_out}"
        }
    },
    # 业务层调用示例（异步通知）:
    # await send_to_mc_async_notification(
    #     "mc.title",
    #     title="服务器公告",
    #     subtitle="即将维护",
    #     fade_in=20,
    #     stay=80,
    #     fade_out=20
    # )

    # --------------------------------------------------------
    # ActionBar 消息接口（send_actionbar）
    # --------------------------------------------------------
    "mc.actionbar": {
        "api": "send_actionbar",
        "data": {
            "message": [
                { "text": "{content}", "color": "aqua" }
            ]
        }
    },
    # 业务层调用示例（异步通知）:
    # await send_to_mc_async_notification(
    #     "mc.actionbar",
    #     content="欢迎来到服务器"
    # )

    # --------------------------------------------------------
    # RCON 命令接口（send_rcon_command）
    # --------------------------------------------------------
    "mc.rcon": {
        "api": "send_rcon_command",
        "data": {
            "command": "{command}"
        }
    }
    # 业务层调用示例（API 调用，等待返回）:
    # result = await call_mc_plugin_api(
    #     "mc.rcon",
    #     {
    #         "command": "list"
    #     }
    # )
    # print(result["data"])
}


# ============================================================
# MC Plugin (QueQiao) 原始接口文档
# ============================================================
# 接口名称: 广播消息接口（broadcast）
# 字段描述:
# 字段路径	类型	 默认值            说明
# message	json   -   消息内容。参考 Minecraft 文本组件。
# 消息格式:
# 发送的聊天消息会在前方添加前缀，默认为：[鹊桥]
# {
#     "api": "broadcast",
#     "data": {
#         "message": [
#             {
#                 "text": " [群名1]",
#                 "color": "aqua"
#             },
#             {
#                 "text": " 用户",
#                 "color": "green"
#             },
#             {
#                 "text": "说:",
#                 "color": "white"
#             },
#             {
#                 "text": "聊天内容",
#                 "color": "white"
#             }
#         ]
#     },
#     "echo": "1"
# }
# 返回信息:
# {
#     "code": 200,
#     "api": "broadcast",
#     "post_type": "response",
#     "status": "SUCCESS",
#     "message": "success",
#     "echo": "1"
# }
#
# 接口名称: 私聊消息接口（send_private_msg）
# 字段描述:
# 字段路径	类型	   默认值  说明
# uuid	string	 -	  接收者 UUID（优先使用），可选，如果为空则使用 nickname。
# nickname	string	-	接收者昵称，当 uuid 为空时使用。
# message	json	-	私聊消息内容。参考 Minecraft 文本组件。
# 发送的聊天消息会在前方添加前缀，默认为：[鹊桥]
# uuid 与 nickname 至少传递一个 若都传递，则优先使用 uuid
# 消息格式:
# {
#     "api": "send_private_msg",
#     "data": {
#         "uuid": null,
#         "nickname": "17TheWord",
#         "message": [
#             {
#                 "text": "[私聊消息]",
#                 "color": "aqua"
#             },
#             {
#                 "text": "说:",
#                 "color": "white"
#             },
#             {
#                 "text": "聊天内容",
#                 "color": "white"
#             }
#         ]
#     },
#     "echo": "1"
# }
# 返回信息:
# 正常发送:
# {
#     "code": 200,
#     "api": "send_private_msg",
#     "post_type": "response",
#     "status": "SUCCESS",
#     "message": "success",
#     "data": {
#         "target_player": {
#             "nickname": "string",
#             "uuid": "string",
#             "is_op": true,
#             "address": "string",
#             "health": 0,
#             "max_health": 0,
#             "experience_level": 0,
#             "experience_progress": 0,
#             "total_experience": 0,
#             "walk_speed": 0,
#             "x": 0,
#             "y": 0,
#             "z": 0
#         },
#         "message": "Send private message success."
#     },
#     "echo": "1"
# }
# uuid/nickname 均为空:
# {
#     "code": 400,
#     "api": "send_private_msg",
#     "post_type": "response",
#     "status": "FAILED",
#     "message": "success",
#     "data": null,
#     "echo": "1"
# }
#
# 接口名称: 标题推送接口（send_title）
# 字段描述:
# 字段路径	  类型	  默认值	 说明
# title	  json	    -	 主标题，参考 Minecraft 文本组件。
# subtitle  json	    -	 副标题，可选，参考 Minecraft 文本组件。
# fade_in	  integer	20	 标题淡入时间，单位 ticks（1 秒 = 20 ticks）。
# stay	  integer	70	 标题停留时间，单位 ticks。
# fade_out  integer	20	 标题淡出时间，单位 ticks。
# Title 与 SubTitle 至少传递一个
# 消息格式:
# {
#     "api": "send_title",
#     "data": {
#         "title": {
#             "text": "Title",
#             "color": "aqua"
#         },
#         "subtitle": {
#             "text": "Sub Title"
#         },
#         "fade_in": 20,
#         "stay": 70,
#         "fade_out": 20
#     },
#     "echo": "1"
# }
# 返回信息:
# {
#     "code": 200,
#     "api": "send_title",
#     "post_type": "response",
#     "status": "SUCCESS",
#     "message": "success",
#     "echo": "1"
# }
#
# 接口名称: 状态栏消息接口（send_actionbar）
# 字段描述:
# 字段路径	类型	 默认值	说明
# message	json   -	ActionBar 消息内容。参考 Minecraft 文本组件。
# 消息格式:
# {
#     "api": "send_actionbar",
#     "data": {
#         "message": [
#             {
#                 "text": "actionbar message",
#                 "color": "aqua"
#             }
#         ]
#     },
#     "echo": "1"
# }
# 返回信息:
# {
#     "code": 200,
#     "api": "send_actionbar",
#     "post_type": "response",
#     "status": "SUCCESS",
#     "message": "success",
#     "echo": "1"
# }
#
# 接口名称: 远程控制命令接口（send_rcon_command）
# 字段描述:
# 字段路径	类型	   默认值  说明
# command	string	 -	  要执行的 RCON 命令字符串。
# 消息格式:
# {
#     "api": "send_rcon_command",
#     "data": {
#         "command": "list"
#     },
#     "echo": "1"
# }
# 返回信息:
# {
#     "code": 200,
#     "api": "send_rcon_command",
#     "post_type": "response",
#     "status": "SUCCESS",
#     "message": "success",
#     "data": "There are 0 of a max of 20 players online: ",
#     "echo": "1"
# }