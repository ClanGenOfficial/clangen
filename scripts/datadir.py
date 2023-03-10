from platformdirs import *


def get_data_dir():
    return user_data_dir('ClanGen', 'ClanGen')


def get_log_dir():
    return get_data_dir() + '/logs'


def get_save_dir():
    return get_data_dir() + '/saves'
