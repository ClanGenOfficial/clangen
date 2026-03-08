import sys
import os
from platformdirs import user_data_dir as _user_data_dir

IS_IOS = getattr(sys, "platform", "") == "ios"

def user_data_dir(appname=None, appauthor=None, version=None, roaming=False):
    if IS_IOS:
        # On iOS, the app's Documents directory is the standard location for user-accessible data
        return os.path.join(os.environ.get("HOME", "."), "Documents")
    return _user_data_dir(appname, appauthor, version, roaming)
