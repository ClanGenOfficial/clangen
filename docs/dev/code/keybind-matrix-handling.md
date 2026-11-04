# Keybind Matrix Map
Our UI can create matrix maps of the interactable elements on the screen through a universal `Screens` function. This map then allows the player to utilize the arrow keys of their keyboard to move through the screen's elements fluidly, with the enter key allowing them to interact with a selected element.

Screens need to be set up with this matrix map in order for the keybinding to work. 

1. Any interactable elements need to be added to the matrix map. Within the `screen_switches` func, you should compile all interactable elements into a list called `interactive_elements`. 
2. This list can then be passed into the `self.add_to_map` function. The function will generate a new `self.matrix_map` for the screen.
3. An element should be designated as the "starting" focus by setting the `self.current_focus` of the screen to the desired element.

If elements aren't being added or removed during screen-use, then you're finished. Nothing else needs to be done, the screen will now work with matrix keybinds.

However, if elements are being added or removed, then you'll need to be updating the map periodically as you do so.

1. When elements are added, pass a list of them through `self.add_to_map` and the map will be updated.
2. When elements are removed, pass a list of them through `self.remove_from_map` before they are killed.
3. The map will have been updated and no further action from you is required.

!!! tip
    You don't have to worry about adding and removing elements if they're being temporarily disabled or hidden. The map automatically skips over "invalid" elements when searching for a new element to focus on.

## Fine Control
If you feel that the auto-generated map isn't lining up with intuitive navigation, you can determine finer control via `focus_map` attributes.

!!! note
    This only works for our custom elements. pygame-gui base element classes will not be capable of this functionality.

    Likewise, not all custom element classes may feature this functionality. Always check if the class has a `focus_map` parameter.

On applicable events, you can pass the `focus_map` argument or access the instance attribute `focus_map` to adjust it. `focus_map` takes an `ElementFocusMap` `TypedDict`. This means you can either pass an `ElementFocusMap` object like so:

```python
element.focus_map = ElementFocusMap(focus_down: other_element)
```

Or you can pass it as a normal dictionary:

```python
element.focus_map = {"focus_down": other_element}
```

Allowed dictionary keys are:

```python
focus_map_dictionary = {
    "focus_down": element,
    "focus_up": element,
    "focus_right": element,
    "focus_left": element
}
```

Each key corresponds to an `Action` direction. When a player presses a key linked to `Action.UP`, the focus will move from the current element to the element above it **OR**, if a `focus_up` value was given, it will move to that value.

In this fashion, we can have finer control over which elements lead to which. However, take care, you can only indicate one element for each focus direction. If elements are being hidden, disabled, or killed during the usage of the screen, you may need to change the focus map accordingly.


