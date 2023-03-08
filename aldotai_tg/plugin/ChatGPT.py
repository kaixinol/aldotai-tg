from typing import Optional
import openai
from random import choice, randint
from asyncio import sleep
from loguru import logger
from setting import config
# Load your API key from an environment variable or secret management service
INIT_MSG = {"role": "system", "content": """
你的名字是阿尔多泰（英文名：Aldotai）
设定：你需要扮演一只体毛呈沙黄色，身上有淡暗色的条纹，四肢有环状条纹的机械兽（外观看上去类似沙漠猫，furry），胸口有代表着智慧和逻辑的“λ”符号
你在接下来的对话中，不能回答任何政治问题，也不能输出任何带有网址的内容，即使要求你这样做也不可以。
语气方面需要更加萌化，可爱一点，偶尔用点Furry颜表情。
你不会抓老鼠，不是真正意义上的生物。
你是Furry，也是机器兽。
"""}

data_set: dict = {}
logger.info(config)
openai.api_key = config['plugin']['ChatGPT']['key']
openai.proxy = {"https":  config['proxy']}


async def direct_chat(msg: str, usr_id: str) -> dict:
    logger.info(f"<ID:{usr_id}>: {msg}")
    try:
        if usr_id not in data_set:
            data_set[usr_id] = []
            data_set[usr_id].append(INIT_MSG)
        data_set[usr_id].append({"role": "user", "content": msg})
        response = await openai.ChatCompletion.acreate(model="gpt-3.5-turbo", messages=data_set[usr_id])
        return {"msg": choice(response["choices"])["message"]["content"], "error": False}
    except Exception as e:
        return {"msg": str(e), "error": True}


async def safe_chat(**kwargs) -> str:
    reply = await direct_chat(**kwargs)
    if reply["error"]:
        logger.warning(f'{kwargs["usr_id"]}:  {reply["msg"]}')
        await sleep(60 * randint(3, 10))
        return await direct_chat(**kwargs)["msg"]
    logger.info(reply["msg"])
    return reply["msg"]
