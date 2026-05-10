# Keybind Matrix Map
Our UI can create matrix maps of the interactable elements on the screen through a universal `Screens` function. This map then allows the player to utilize the arrow keys of their keyboard to move through the screen's elements fluidly, with the enter key allowing them to interact with a selected element.

Screens need to be set up with this matrix map in order for the keybinding to work. 

1. Any interactable elements need to be added to the matrix map. Within the `screen_switches` func, you should compile all interactable elements into a list called `elements_list`. 
2. This list can then be passed into the `self.update_map` function. The function will generate a new `self.matrix_map` for the screen.
3. The `handle_event` func needs to properly detect `enter` key usage and pass the event as required. Generally, anywhere that we detect a `UI_BUTTON_START_PRESS` or similar actions, we also need to check for `KEYDOWN` actions like so:

```py
    def handle_event(self, event):
      if event.type == pygame_gui.UI_BUTTON_START_PRESS or (
          event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
      ): # (1)
          if event.type == pygame.KEYDOWN:
              element = self.current_selection  # (2)
          else:
              element = event.ui_element
          
          if element == self.element_on_the_screen:  # (3)
              do_something()
          
```

1.  `event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN` allows us to detect that the `enter` button was pressed down, which we must treat the same as a normal button click.
2. If this is a `KEYDOWN` event, then we need to check the element currently being selected via keybinds. `self.current_selection` is that element. We "replace" the event element with this in order to interact with the selected element. `self.current_selection` is automatically updated every time arrow keybinds are pressed.
3. This means that rather than checking `event.ui_element` as we usually do, you should be checking `element` throughout `handle_event()`.

If elements aren't being added or removed during screen-use, then you're finished. Nothing else needs to be done, the screen will now work with matrix keybinds.


However, if elements are being added or removed, then you'll need to be updating the map periodically through the same function.

1. When elements are added, pass a list of them through `self.update_map` and the map will be updated.
2. When elements are removed, pass a list of them through `self.update_map` before they are killed. Be sure to set the arg `remove` to True.
3. The map will have been updated and no further action from you is required.
