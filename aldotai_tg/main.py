from aiogram import Bot, Dispatcher, executor, types
from loguru import logger

from plugin.ChatGPT import chat, data_set
from setting import config
from asyncio import sleep

bot = Bot(token=config['telegramToken'], proxy=config['proxy'])
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply('''
/forgetme clears previous dialogue memory
/help display help information
source code:
https://github.com/kaixinol/aldotai-tg
''')


@dp.message_handler(commands=["forgetme"])
async def send_welcome(message: types.Message):
    if message.chat.type == 'private':
        if f'{message.from_user.username}+{message.from_user.id}' in data_set:
            del data_set[f'{message.from_user.username}+{message.from_user.id}']
            await message.reply("阿尔多泰已经忘了之前发生的事啦")
            return
        await message.reply("阿尔多泰不记得有发生什么对话")


@dp.message_handler()
async def say(message: types.Message):
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
