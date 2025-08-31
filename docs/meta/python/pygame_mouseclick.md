# Pygame Mouse click (mousedown)

In Pygame, there is no specific event like `MOUSEBUTTONCLICK` that directly represents a mouse click. However, you can achieve the desired behavior by handling `MOUSEBUTTONDOWN` events and tracking the state of the mouse button. Here's a simple approach:

```python
import pygame
import sys

pygame.init()

# Set up the display
width, height = 400, 300
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Mouse Click Example")

# Set up some colors
white = (255, 255, 255)
black = (0, 0, 0)

# Set up the clock to control the frame rate
clock = pygame.time.Clock()

# Main game loop
running = True
mouse_button_down = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_button_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                mouse_button_down = False

    # Clear the screen
    screen.fill(white)

    # Draw a rectangle if the mouse button is down
    if mouse_button_down:
        pygame.draw.rect(screen, black, (50, 50, 100, 100))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
sys.exit()
```

In this example, we use the `MOUSEBUTTONDOWN` and `MOUSEBUTTONUP` events to track the state of the left mouse button (`event.button == 1`). When the left mouse button is pressed, `mouse_button_down` is set to `True`, and when it's released, `mouse_button_down` is set to `False`. This way, you can respond to the start and end of a mouse click without flickering issues.
