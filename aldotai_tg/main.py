from aiogram import Bot, Dispatcher, executor, types
from plugin.ChatGPT import safe_chat, data_set
from setting import config

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
        await message.reply(
            await safe_chat(msg=message.text, usr_id=f'{message.from_user.username}+{message.from_user.id}'))


executor.start_polling(dp, skip_updates=True)
