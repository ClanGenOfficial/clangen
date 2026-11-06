from pathlib import Path
import plistlib


def get_icon(app_path):
    app_path_obj = Path(app_path)
    plist_path = app_path_obj.joinpath("Contents", "Info.plist")
    with open(plist_path, "rb") as f:
        plist = plistlib.load(f)
    icon_name = plist["CFBundleIconFile"]
    return str(app_path_obj.joinpath("Contents", "Resources", icon_name))


application = "dist/Clangen.app"
badge_icon = get_icon(application)

background = "resources/images/mac_installer_bg_blank.png"

format = "UDBZ"

files = [application]
symlinks = {"Applications": "/Applications"}
icon_locations = {"Clangen.app": (66, 200), "Applications": (204, 200)}

window_rect = ((100, 100), (600, 500))

default_view = "icon-view"
arrange_by = None
grid_offset = (0, 0)
grid_spacing = 100
scroll_position = (0, 0)
label_pos = "bottom"
text_size = 12
icon_size = 75
