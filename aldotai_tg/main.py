import hashlib
from os import getcwd, popen
import tempfile
from aiogram import Bot, Dispatcher, executor, types
from loguru import logger

from plugin.ChatGPT import chat, data_set
from plugin.YamlBuilder import to_yaml
import setting
from asyncio import sleep
from base64 import b64decode

bot = Bot(token=setting.config['telegramToken'], proxy=setting.config['proxy'])
dp = Dispatcher(bot)
logger.add(
    getcwd() + "/log/{time:YYYY-MM-DD}.log",
    rotation="00:00",
    level="ERROR",
    encoding="utf-8",
)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply('''
/forgetme clears previous dialogue memory
/help display help information
/yaml generate FGI yaml data files. See github: FurryGamesIndex/games
source code:
https://github.com/kaixinol/aldotai-tg
''')


@dp.message_handler(commands=["forgetme"])
async def forgetme(message: types.Message):
    if message.chat.type == 'private':
        if f'{message.from_user.username}+{message.from_user.id}' in data_set:
            del data_set[f'{message.from_user.username}+{message.from_user.id}']
            await message.reply("阿尔多泰已经忘了之前发生的事啦")
            return
        await message.reply("阿尔多泰不记得有发生什么对话")


@dp.message_handler(commands=["debug"])
async def debug(message: types.Message):
    def exec_cmd(cmd):
        r = popen(cmd)
        text = r.read()
        r.close()
        return text

    def genearte_MD5(s: str):
        hl = hashlib.md5()
        hl.update(s.encode(encoding='utf-8'))
        return hl.hexdigest()

    if message.chat.type == 'private' and message.from_user.username == setting.config["admin"]:
        try:
            code = b64decode(message.text[6:].encode()).decode()
            file_path=tempfile.gettempdir() + "/" + genearte_MD5(code) + ".py"
            with open(file_path, 'w+') as f:
                f.write(code)
                f.close()
            await message.reply(exec_cmd(f"python {file_path}"))
        except Exception as e:
            await message.reply(str(e))


@dp.message_handler(commands=["yaml"])
async def yaml(message: types.Message):
    if message.chat.type == 'private':
        try:
            logger.info(f'<{message.from_user.username}>:{message.text[6:]}')
            await message.reply_document(**await to_yaml(message.from_user.id, message.text[6:]))
        except Exception as e:
            logger.error(str(e))
            await message.reply(f'发生了错误，已记录此错误信息：`{str(e)}`', parse_mode="Markdown")


@dp.message_handler()
async def gpt(message: types.Message):
    if message.chat.type == 'private' and message.text[0] != "/":
        usr_id = f'{message.from_user.username}+{message.from_user.id}'
        reply = await chat(msg=message.text, usr_id=usr_id)
        if reply['error']:
            msg_id = await message.reply(f'阿尔多泰现在不可用。以下是错误信息：\n`{reply["msg"]}`', parse_mode="Markdown")
            logger.warning(f'阿尔多泰现在不可用。以下是错误信息：\n`{reply["msg"]}`')
            await sleep(10)
            await bot.delete_message(message_id=msg_id["message_id"], chat_id=message.chat.id)
            return
        await message.reply(reply["msg"])
        logger.info(reply["msg"])
        data_set[usr_id].append({"role": "assistant", "content": reply["msg"]})


executor.start_polling(dp, skip_updates=True)
