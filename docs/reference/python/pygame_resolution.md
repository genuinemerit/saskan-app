# Pygame Screen Resolution setting

In Pygame, you can adjust the resolution of the display by setting the width and height parameters when creating the screen surface using `pygame.display.set_mode()`. To ensure that the game looks consistent across different resolutions, you can use a fixed resolution and scale the graphics accordingly. Here's an example:

```python
import pygame
import sys

# Set a fixed resolution for your game
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

def main():
    pygame.init()

    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Your game logic and drawing code here

        pygame.display.flip()
        clock.tick(60)  # Adjust the frame rate as needed

if __name__ == "__main__":
    main()
```

In this example, the game window is set to a fixed resolution of 800x600. You can design your game graphics and elements based on this resolution. When rendering, you can scale the graphics to fit the actual window size by using the `pygame.transform.scale()` function. This way, your game should look consistent across different resolutions.

```python
scaled_image = pygame.transform.scale(original_image, (new_width, new_height))
```

Adjust the `new_width` and `new_height` based on the actual window size. Keep in mind that scaling graphics may result in a loss of quality, so it's a good practice to design your assets for the target resolution.

Additionally, you may want to handle aspect ratios to avoid stretching or distorting the graphics. You can calculate the scaling factors for width and height based on the ratio between the fixed resolution and the actual resolution.

---

## Get info on screen resolution

Yes, you can determine the resolution of the display using Python, specifically by using the `pygame.display.Info()` object from the Pygame library. Here's an example:

```python
import pygame

def get_display_resolution():
    pygame.init()

    # Get information about the default display
    info = pygame.display.Info()

    # Display the resolution
    print("Display Width:", info.current_w)
    print("Display Height:", info.current_h)

    pygame.quit()

if __name__ == "__main__":
    get_display_resolution()
```

This script initializes Pygame, retrieves information about the default display, and prints the current width and height. Note that this is the resolution of the primary display.

Keep in mind that if you haven't set up Pygame on your system, you may need to install it first using:

```bash
pip install pygame
```

If you're not specifically tied to Pygame, you can also use the `screeninfo` library to get information about the screen. Install it using:

```bash
pip install screeninfo
```

Here's an example using `screeninfo`:

```python
from screeninfo import get_monitors

def get_display_resolution():
    monitors = get_monitors()

    for monitor in monitors:
        print("Monitor Width:", monitor.width)
        print("Monitor Height:", monitor.height)

if __name__ == "__main__":
    get_display_resolution()
```

This script uses the `get_monitors()` function from the `screeninfo` library to retrieve information about all connected monitors and prints their respective resolutions.
