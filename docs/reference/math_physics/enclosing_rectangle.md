# Enclosing rectangle of a sphere

To derive the dimensions of the enclosing rectangle of a sphere with a given radius $r$, you can use some basic geometric principles. The enclosing rectangle will have dimensions equal to $2r$ in all three dimensions (length, width, and height). This is because, by definition, the sphere's diameter is twice the radius.

Here's an example in Python to calculate and visualize the enclosing rectangle of a sphere:

```python
import matplotlib.pyplot as plt
import numpy as np

# Sphere radius
r = 5.0

# Calculate the dimensions of the enclosing rectangle
length = width = height = 2 * r

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Create a grid of points for the sphere's surface
u = np.linspace(0, 2 * np.pi, 100)
v = np.linspace(0, np.pi, 100)
x = r * np.outer(np.cos(u), np.sin(v))
y = r * np.outer(np.sin(u), np.sin(v))
z = r * np.outer(np.ones(np.size(u)), np.cos(v))

# Draw the sphere
ax.plot_surface(x, y, z, color='b', alpha=0.6)

# Set the axis limits based on the enclosing rectangle dimensions
ax.set_xlim([0, length])
ax.set_ylim([0, width])
ax.set_zlim([0, height])

# Set labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

plt.show()

```

In this example:

* We specify the radius of the sphere ($r$) as `r`.
* We calculate the dimensions of the enclosing rectangle, where `length`, `width`, and `height` are all equal to `2 * r`.
* We create a 3D plot using `matplotlib` and `mpl_toolkits.mplot3d`.
* We draw the sphere and set its color to blue.
* We set the axis limits based on the enclosing rectangle dimensions.
* We label the axes as X, Y, and Z.

This code visually demonstrates the enclosing rectangle of the sphere with the specified radius. Adjust the `r` variable to change the sphere's radius and see how the enclosing rectangle dimensions change accordingly.
