from platformdirs import *


def get_save_dir():
    return user_data_dir('Clangen', 'Clangen') + '/saves'