import datetime

from .colors import BColors


def print_info(info_string):
    print("                                                                                                          \r"
          "{}{}[INFO]  {}{}{}".format(BColors.PURPLE, timestamp(), BColors.WHITE, info_string, BColors.RESET))


def print_error(err_string):
    print("{}{}[ERROR] {}{}".format(BColors.RED, timestamp(), err_string, BColors.RESET))


def timestamp():
    x = datetime.datetime.now()
    return x.strftime('[%d.%m.%y %H:%M:%S]')
