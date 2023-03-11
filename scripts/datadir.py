import os

from platformdirs import *

from scripts.version import get_version_info


def setup_data_dir():
    os.makedirs(get_data_dir(), exist_ok=True)
    os.makedirs(get_save_dir(), exist_ok=True)
    os.makedirs(get_log_dir(), exist_ok=True)


def get_data_dir():
    if get_version_info().is_source_build:
        return '.'
    elif not get_version_info().is_release:
        return user_data_dir('ClanGenBeta', 'ClanGen')
    return user_data_dir('ClanGen', 'ClanGen')


def get_log_dir():
    return get_data_dir() + '/logs'


def get_save_dir():
    return get_data_dir() + '/saves'
