from scripts.ui.elements.image_button import UIImageButton


class CatButton(UIImageButton):
    """Basic UIButton subclass for at sprite buttons. It stores the cat ID.
    Can also be used as a general button that holds some data"""

    def __init__(
        self,
        relative_rect,
        text,
        cat_id=None,
        visible=True,
        cat_object=None,
        starting_height=1,
        parent_element=None,
        object_id=None,
        manager=None,
        tool_tip_text=None,
        text_kwargs=None,
        tool_tip_text_kwargs=None,
        container=None,
        anchors=None,
        mask=None,
        mask_padding=None,
        auto_disable_if_no_data=False,
        tool_tip_object_id=None,
    ):
        self.cat_id = cat_id
        self.cat_object = cat_object

        super().__init__(
            relative_rect,
            text,
            text_kwargs=text_kwargs,
            tool_tip_text_kwargs=tool_tip_text_kwargs,
            object_id=object_id,
            visible=visible,
            parent_element=parent_element,
            starting_height=starting_height,
            manager=manager,
            tool_tip_text=tool_tip_text,
            container=container,
            anchors=anchors,
            allow_double_clicks=True,
            mask=mask,
            mask_padding=mask_padding,
            tool_tip_object_id=tool_tip_object_id,
        )
        if auto_disable_if_no_data and cat_id is None and cat_object is None:
            self.disable()

    def return_cat_id(self):
        return self.cat_id

    def return_cat_object(self):
        return self.cat_object

    def set_id(self, id):
        self.cat_id = id
