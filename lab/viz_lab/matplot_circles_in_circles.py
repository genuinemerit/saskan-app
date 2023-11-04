import matplotlib.pyplot as plt

"""
Note that given the vast spaces, an attempt to represent a galactic cluster
within the universe may result in a dot tinier than can be represented in
a single pixel.
"""

# Circle A
radius_A = 1000
center_A = (0, 0)

# Circle B
radius_B = 100  # Smaller radius for visualization
offset_x = 670
offset_y = -420
center_B = (offset_x, offset_y)
# center_B = (0, 0)

# Create a figure and axis
fig, ax = plt.subplots()

# Plot circle A
circle_A = plt.Circle(center_A, radius_A, color='blue', fill=False, label='Circle A')
ax.add_artist(circle_A)

# Plot circle B
circle_B = plt.Circle(center_B, radius_B, color='red', fill=True, label='Circle B')
ax.add_artist(circle_B)

# Set axis limits
ax.set_xlim(-radius_A, radius_A)
ax.set_ylim(-radius_A, radius_A)

# Add labels and legend
plt.xlabel('X (Units)')
plt.ylabel('Y (Units)')
plt.title('Circle A and Circle B')
plt.legend()

# Show the plot
plt.grid(True)
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
