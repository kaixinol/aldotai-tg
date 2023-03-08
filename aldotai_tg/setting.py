from yaml import safe_load
from loguru import logger

config = {}
try:
    with open("config.yaml") as fp:
        config = safe_load(fp)
except Exception as e:
    logger.error(e)