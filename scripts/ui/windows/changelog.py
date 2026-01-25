import subprocess

import pygame
from scripts.game_structure.screen_settings import MANAGER
from scripts.game_structure.ui_elements import UITextBoxTweaked
from scripts.housekeeping.version import get_version_info
from scripts.ui.windows.window_base_class import GameWindow
from scripts.utility import ui_scale
from re import search as re_search


class ChangelogWindow(GameWindow):
    def __init__(self):
        super().__init__(
            ui_scale(pygame.Rect((150, 150), (500, 400))),
        )

        self.changelog_popup_title = UITextBoxTweaked(
            "windows.whats_new",
            ui_scale(pygame.Rect((0, 10), (500, -1))),
            line_spacing=1,
            object_id="#changelog_popup_title",
            container=self,
            anchors={"centerx": "centerx"},
        )

        current_version_number = "{:.16}".format(get_version_info().version_number)

        self.changelog_popup_subtitle = UITextBoxTweaked(
            "windows.version_title",
            ui_scale(pygame.Rect((0, 35), (500, -1))),
            line_spacing=1,
            object_id="#changelog_popup_subtitle",
            container=self,
            anchors={"centerx": "centerx"},
            text_kwargs={"ver": current_version_number},
        )

        dynamic_changelog = False
        if (
            get_version_info().is_dev()
            and get_version_info().is_source_build
            and get_version_info().git_installed
        ):
            file_cont = subprocess.check_output(
                [
                    "git",
                    "log",
                    r"--pretty=format:%H|||%cd|||%b|||%s",
                    "-15",
                    "--no-decorate",
                    "--merges",
                    "--grep=Merge pull request",
                    "--date=short",
                ]
            ).decode("utf-8")
            dynamic_changelog = True
        else:
            with open("changelog.txt", "r", encoding="utf-8") as read_file:
                file_cont = read_file.read()

        if get_version_info().is_dev() and not get_version_info().is_source_build:
            dynamic_changelog = True

        if dynamic_changelog:
            commits = file_cont.splitlines()
            file_cont = ""
            for line in commits:
                info = line.split("|||")

                if len(info) < 4:
                    continue

                # Get PR number so we can link the PR
                pr_number = re_search(r"Merge pull request #([0-9]*?) ", info[3])
                if pr_number:
                    # For some reason, multi-line links on pygame_gui's text boxes don't work very well.
                    # So, to work around that, just add a little "link" at the end
                    info[
                        2
                    ] += f" <a href='https://github.com/ClanGenOfficial/clangen/pull/{pr_number.group(1)}'>(link)</a>"

                # Format: DATE- \n PR Title (link)
                file_cont += f"<b>{info[1]}</b>\n- {info[2]}\n"

        self.changelog_text = UITextBoxTweaked(
            file_cont,
            ui_scale(pygame.Rect((10, 65), (480, 325))),
            object_id="#text_box_30",
            line_spacing=0.95,
            starting_height=2,
            container=self,
            manager=MANAGER,
        )
