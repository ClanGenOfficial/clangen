import os

from platformdirs import *


def setup_data_dir():
    os.makedirs(get_data_dir(), exist_ok=True)
    os.makedirs(get_save_dir(), exist_ok=True)
    os.makedirs(get_log_dir(), exist_ok=True)


def get_data_dir():
    return user_data_dir('ClanGen', 'ClanGen')


def get_log_dir():
    return get_data_dir() + '/logs'


def get_save_dir():
    return get_data_dir() + '/saves'
