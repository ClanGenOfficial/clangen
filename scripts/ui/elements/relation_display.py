import i18n
import pygame
import pygame_gui

from scripts.cat_relations.enums import RelType
from scripts.ui.elements.relation_status_fill_bar import UIRelationStatusFillBar
from scripts.ui.elements.relation_status_scale_bar import UIRelationStatusScaleBar
from scripts.ui.elements.text_box_tweaked import UITextBoxTweaked
from scripts.ui.scale import ui_scale


class UIRelationDisplay(pygame_gui.elements.UIAutoResizingContainer):
    def __init__(
        self,
        position: tuple,
        relationship,
        romance: bool = False,
        container=None,
        manager=None,
        anchors=None,
        starting_height=1,
    ):
        dimensions = (0, 0)
        self.rel_elements = {}
        bar_size = (96, 10)

        super().__init__(
            relative_rect=ui_scale(pygame.Rect(position, dimensions)),
            container=container,
            manager=manager,
            anchors=anchors,
            starting_height=starting_height,
        )

        prev_element = None
        for rel_type in [*RelType]:
            if rel_type == RelType.ROMANCE:
                continue
            num, tier = relationship.get_rel_type_attributes(rel_type)
            self.rel_elements[f"{rel_type}_text"] = pygame_gui.elements.UITextBox(
                f"relationships.{tier}",
                ui_scale(
                    pygame.Rect(
                        (0 - 2, 0),
                        (100, 25),
                    )
                ),
                object_id="#text_box_26_horizcenter",
                container=self,
                anchors={"top_target": prev_element} if prev_element else None,
            )
            self.rel_elements[f"{rel_type}_text"].set_tooltip(
                i18n.t(f"relationships.{rel_type}", count=num)
            )
            self.rel_elements[f"{rel_type}_text"].tool_tip_delay = 0
            self.rel_elements[f"{rel_type}_text"].disable()
            self.rel_elements[f"{rel_type}_bar"] = UIRelationStatusScaleBar(
                ui_scale(pygame.Rect((0, -5), bar_size)),
                tier,
                anchors={"top_target": self.rel_elements[f"{rel_type}_text"]},
                scale_position=num,
                container=self,
            )
            prev_element = self.rel_elements[f"{rel_type}_bar"]

            # ROMANCE
        if romance:
            self.rel_elements[f"romance_text"] = UITextBoxTweaked(
                f"relationships.{relationship.romance_tier if relationship.romance_tier else 'neutral'}",
                ui_scale(
                    pygame.Rect(
                        (0, 1),
                        (96, -1),
                    )
                ),
                object_id="#text_box_26_horizcenter",
                anchors={"top_target": prev_element},
                container=self,
                line_spacing=0.95,
            )
            self.rel_elements[f"romance_text"].set_tooltip(
                i18n.t(f"relationships.romance", count=relationship.romance)
            )
            self.rel_elements[f"romance_text"].tool_tip_delay = 0
            self.rel_elements[f"romance_text"].disable()
            self.rel_elements[f"romance_text"].disable()
            self.rel_elements[f"romance_bar"] = UIRelationStatusFillBar(
                ui_scale(
                    pygame.Rect(
                        (0, -5),
                        bar_size,
                    )
                ),
                relationship.romance,
                container=self,
                anchors={"top_target": self.rel_elements[f"romance_text"]},
            )

        self.romance = romance
