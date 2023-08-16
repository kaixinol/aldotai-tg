from json import load, dump
from os.path import exists

ban_bot = []
if not exists("bot.json"):
    with open("bot.json", "w") as fp:
        dump([], fp)
else:
    with open("bot.json", "r") as fp:
        ban_bot = load(fp)


def ban(bot_name: str):
    if bot_name not in ban_bot:
        with open("bot.json", "w") as fp:
            ban_bot.append(bot_name)
            dump(ban_bot, fp)


def unban(bot_name: str):
    if bot_name in ban_bot:
        with open("bot.json", "w") as fp:
            ban_bot.pop(bot_name)
            dump(ban_bot, fp)
