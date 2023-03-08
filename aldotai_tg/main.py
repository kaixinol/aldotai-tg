from aiogram import Bot, Dispatcher, executor, types
from plugin.ChatGPT import safe_chat
from setting import config

bot = Bot(token=config['telegramToken'], proxy=config['proxy'])
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi! I am aldotai bot :)")


@dp.message_handler()
async def say(message: types.Message):
    if message.chat.type == 'private':
        await message.reply(await safe_chat(msg=message.text, usr_id=str(message.from_user.id)))


executor.start_polling(dp, skip_updates=True)
