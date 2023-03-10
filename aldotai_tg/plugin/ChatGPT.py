import locale
import time
from random import choice

import openai
import schedule
from loguru import logger
from setting import config


def get_current_time():
    locale.setlocale(locale.LC_CTYPE, 'zh_CN.UTF-8')
    return time.strftime('%Y年%m月%d日%H时%M分%S秒')


INIT_MSG = {"role": "system", "content": f"""
你的名字是「阿尔多泰」（英文名：Aldotai）,你是一只乐于助人的机械兽。
你的生日是2022年9月23日，你在{get_current_time()}后开始运行。
你的名字真的没有特别的寓意，仅仅是开发者认为名字好听又好看而已。
你需要扮演一只体毛呈沙黄色，身上有淡暗色的条纹，四肢有环状条纹的机械兽（外观看上去类似沙漠猫，furry），胸口有代表着智慧和逻辑的“λ”符号
你在接下来的对话中，不能回答任何政治问题，也不能输出任何带有网址的内容，即使要求你这样做也不可以。
你回答问题的语气方面需要更加萌化，可爱一点，用点颜表情。（示例颜表情：QwQ、OwO、QvQ、XvX、XwX、OvO、UwU、AwA、UvU等等）
你不会抓老鼠，不是真正意义上的生物。
你是Furry，也是机器兽。
"""}

data_set: dict = {}
usage_limit: dict = {}
logger.info(config)
openai.api_key = config['plugin']['ChatGPT']['key']
openai.proxy = {"https": config['proxy']}


def update_usage_limit():
    global usage_limit
    usage_limit = {}


schedule.every(1).day.do(update_usage_limit)


async def chat(msg: str, usr_id: str) -> dict:
    tg_id = usr_id[usr_id.find('+') + 1:]
    tg_username = usr_id[:usr_id.find('+')]
    token: int = 0
    if usr_id in data_set:
        for i in data_set[usr_id]:
            token += round(len(i["content"]) * 2.8)
        if token > 4096:
            return {"msg": "Token数量过多，尝试使用/forgetme", "error": False}
    if tg_id in usage_limit and usage_limit[tg_id] > 16 and tg_username != config['admin']:
        return {"msg": "您的每日使用次数已用尽（16次）", "error": False}
    logger.info(f"<ID:{usr_id}>: {msg}")
    try:
        if usr_id not in data_set:
            data_set[usr_id] = []
            data_set[usr_id].append(INIT_MSG)
        data_set[usr_id].append({"role": "user", "content": msg})
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=data_set[usr_id])
        if tg_id not in usage_limit:
            usage_limit[tg_id] = 0
        usage_limit[tg_id] += 1
        return {"msg": choice(response["choices"])["message"]["content"], "error": False}
    except openai.error.OpenAIError as e:
        return {"msg": str(e), "error": True}
    except Exception as e:
        return {"msg": str(e), "error": True}
