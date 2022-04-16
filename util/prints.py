import datetime

from .colors import BColors


def print_info(info_string):
    print("{}{}[INFO]  {}{}".format(timestamp(), BColors.PURPLE, BColors.WHITE, info_string))


def print_error(err_string):
    print("{}{}[ERROR] {}".format(timestamp(), BColors.RED, err_string))


def timestamp():
    x = datetime.datetime.now()
    return x.strftime('{}[%d.%m.%y %H:%M:%S]'.format(BColors.PURPLE))
