import logging

bot_err_logger = logging.getLogger('BOT_ERRORS')
bot_err_logger.setLevel(logging.ERROR)
fh = logging.FileHandler('err.log')
sh = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
fh.setFormatter(formatter)
sh.setFormatter(formatter)
bot_err_logger.addHandler(fh)
bot_err_logger.addHandler(sh)




