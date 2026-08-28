from scripts.ui.elements.surface_image_button import UISurfaceImageButton


class IDImageButton(UISurfaceImageButton):
    """Class to handle the "involved cats" button on the events page. It stores the IDs of the cat's involved."""

    def __init__(
        self,
        relative_rect,
        text,
        button_dict,
        ids=None,
        object_id=None,
        container=None,
        manager=None,
        layer_starting_height=1,
        anchors=None,
        parent_element=None,
    ):
        if ids:
            self.ids = ids
        else:
            self.ids = None

        super().__init__(
            relative_rect,
            text,
            image_dict=button_dict,
            object_id=object_id,
            container=container,
            starting_height=layer_starting_height,
            manager=manager,
            anchors=anchors,
            parent_element=parent_element,
        )
        # This button will auto-disable if no ids are entered.
        if not self.ids:
            self.disable()
