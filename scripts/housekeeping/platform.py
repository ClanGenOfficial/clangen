import sys
import os
from platformdirs import user_data_dir as _user_data_dir

IS_IOS = getattr(sys, "platform", "") == "ios"

def user_data_dir(appname=None, appauthor=None, version=None, roaming=False):
    if IS_IOS:
        # Try to get the iCloud Ubiquity container
        try:
            from rubicon.objc import ObjCClass
            NSFileManager = ObjCClass('NSFileManager')
            fileManager = NSFileManager.defaultManager
            
            # This returns the URL for the iCloud container defined in your entitlements
            url = fileManager.URLForUbiquityContainerIdentifier_(None)
            if url:
                # Append 'Documents' to the iCloud path. 
                # Files in the 'Documents' subfolder of the ubiquity container 
                # are automatically visible in the user's iCloud Drive.
                icloud_path = os.path.join(str(url.path), "Documents")
                if not os.path.exists(icloud_path):
                    os.makedirs(icloud_path, exist_ok=True)
                return icloud_path
        except Exception as e:
            # Fallback if rubicon is missing or iCloud is disabled
            print(f"iCloud not available, using local storage: {e}")

        # Fallback to local app Documents directory (On My iPad)
        return os.path.join(os.environ.get("HOME", "."), "Documents")
        
    return _user_data_dir(appname, appauthor, version, roaming)
