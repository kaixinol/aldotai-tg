import re
import sys
import time
from asyncio import sleep
from os import getcwd, popen

from aiogram import Bot, Dispatcher, executor, types
from loguru import logger

from plugin.ChatGPT import chat, data_set
from plugin.Lottery import get_row_count_by_id, insert_info, get_random_records, get_count
from plugin.RestrictBot import ban, unban, ban_bot
from plugin.YamlBuilder import to_yaml
from setting import config

bot = Bot(token=config["telegramToken"], proxy=config["proxy"])
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
    await message.reply(
        """
/forgetme clears previous dialogue memory
/help display help information
/yaml generate FGI yaml data files. See github: FurryGamesIndex/games
source code:
https://github.com/kaixinol/aldotai-tg
"""
    )


@dp.message_handler(commands=["forgetme"])
async def forgetme(message: types.Message):
    if message.chat.type == "private":
        if f"{message.from_user.username}+{message.from_user.id}" in data_set:
            del data_set[f"{message.from_user.username}+{message.from_user.id}"]
            data_set[f"{message.from_user.username}+{message.from_user.id}"] = [INIT_MSG]
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

    def decode_it(s: str):
        byte_data = bytes.fromhex(s)
        return byte_data.decode('utf-8')

    if message.chat.type == "private" and message.from_user.username == config["admin"]:
        try:
            code = decode_it(message.text[6:])
            print(code)
            await message.reply(exec_cmd(f"\"{sys.executable}\" -c \"{code}\"").strip())
        except Exception as e:
            await message.reply(str(e))


@dp.message_handler(commands=["yaml"])
async def yaml(message: types.Message):
    if message.chat.type == "private":
        try:
            logger.info(f"<{message.from_user.username}>:{message.text[6:]}")
            await message.reply_document(
                **await to_yaml(message.from_user.id, message.text[6:])
            )
        except Exception as e:
            logger.error(str(e))
            await message.reply(f"发生了错误，已记录此错误信息：`{str(e)}`", parse_mode="Markdown")


@dp.message_handler(commands=["banbot"])
async def banbot(message: types.Message):
    if "group" in message.chat.type and message.from_user.username == config["admin"]:
        await message.reply("封禁成功！")
        ban(message.text[8:])
    elif "group" in message.chat.type and message.from_user.username != config["admin"]:
        await message.reply("你非管理员")


@dp.message_handler(commands=["unbanbot"])
async def unbanbot(message: types.Message):
    if "group" in message.chat.type and message.from_user.username == config["admin"]:
        await message.reply("解禁成功！")
        unban(message.text[10:])
    elif "group" in message.chat.type and message.from_user.username != config["admin"]:
        await message.reply("你非管理员")


@dp.message_handler(commands=["join_draw"])
async def join_draw(message: types.Message):
    async def check_user_in_channel(user_id_to_check):
        chat_member = await bot.get_chat_member('@furrystickercn', user_id_to_check)
        if chat_member.status == types.ChatMemberStatus.MEMBER or chat_member.status == types.ChatMemberStatus.ADMINISTRATOR:
            return True
        else:
            return False

    if "private" in message.chat.type:
        if get_row_count_by_id(message.from_user.id) and (
                await check_user_in_channel(message.from_user.id) or message.from_user.username == config["admin"]):
            current_milli_time = lambda: int(round(time.time() * 1000))
            insert_info(message.from_user.id, message.from_user.username, current_milli_time())
            await message.reply("Successfully participated in the lucky draw!")
        elif not (await check_user_in_channel(message.from_user.id) or message.from_user.username == config["admin"]):
            await message.reply("You cannot enter the draw because you are not subscribed to @furrystickercn")
        else:
            await message.reply("You have already participated in the lucky draw!")


@dp.message_handler(commands=["open"])
async def open_raffle(message: types.Message):
    def convert(time_stamp: int):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_stamp / 1000)))

    async def get_nickname(user_id):
        user = await bot.get_chat(user_id)
        return user.first_name

    async def get_t_me_link(user_id):
        user = await bot.get_chat(user_id)
        link = await user.get_url()
        return link

    if "private" in message.chat.type:
        if message.from_user.username == config["admin"]:
            nums = [int(num) for num in re.findall(r'\d+', message.text)]
            if len(message.text) < 6 or len(nums) != 2:
                await message.reply("Parameter error")
                return
            records = get_random_records(nums[0])
            if get_count() < nums[1]:
                await message.reply(f"Number of participants less than {nums[1]}")
                return
            msg = ""
            for i in records:
                nickname = await get_nickname(i.id)
                username_part = f"([@{i.user_name}](https://t.me/{i.user_name}))" if i.user_name else " "
                nickname_part = f"[{nickname}]({await get_t_me_link(i.id)})"
                timestamp_str = convert(i.time)
                entry = f"{nickname_part}{username_part} `{timestamp_str}`\n"
                msg += entry
            await message.reply(msg, parse_mode="markdown")


@dp.message_handler()
async def handle_gpt(message: types.Message):
    if (
            message.chat.type == "private"
            and message.text[0] != "/"
            and message.text[0] != "@"
    ):
        usr_id = f"{message.from_user.username}+{message.from_user.id}"
        await message.answer_chat_action("typing")
        reply = await chat(msg=message.text, usr_id=usr_id)
        if reply["error"]:
            msg_id = await message.reply(
                f'阿尔多泰现在不可用。以下是错误信息：\n`{reply["msg"]}`', parse_mode="Markdown"
            )
            logger.warning(f'阿尔多泰现在不可用。以下是错误信息：\n`{reply["msg"]}`')
            await sleep(10)
            await bot.delete_message(
                message_id=msg_id["message_id"], chat_id=message.chat.id
            )
            return
        await message.reply(reply["msg"])
        logger.info(reply["msg"])
        data_set[usr_id].append({"role": "assistant", "content": reply["msg"]})
    elif (
            "via_bot" in message
            and message.from_user.username != config["admin"]
            and message["via_bot"]["username"] in ban_bot
    ):
        await bot.delete_message(
            message_id=message["message_id"], chat_id=message.chat.id
        )
        msg_id = await bot.send_message(
            text=f"@{message.from_user.username} 请勿使用被封禁的bot", chat_id=message.chat.id
        )
        await sleep(5)
        await bot.delete_message(
            message_id=msg_id["message_id"], chat_id=message.chat.id
        )


executor.start_polling(dp, skip_updates=True)
