from loguru import logger
from yaml import safe_load

config = {}
try:
    with open("config.yaml") as fp:
        config = safe_load(fp)
except Exception as e:
    logger.error(e)
