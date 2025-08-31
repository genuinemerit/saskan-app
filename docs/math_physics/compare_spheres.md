# Compare size of spheres

Here's a Python code example to calculate the relative size of Sphere B compared to Sphere A:

```python
import math

# Radius of Sphere A in gigaparsecs
radius_A_gp = 14.25

# Radius of Sphere B in light years
radius_B_ly = 10000  # For example, 10,000 light years

# Calculate the volumes of both spheres
volume_A = (4/3) * math.pi * (radius_A_gp**3)
volume_B = (4/3) * math.pi * ((radius_B_ly / 3.09e19)**3)  # Convert light years to gigaparsecs

# Calculate the percentage of B compared to A
percentage_B_to_A = (volume_B / volume_A) * 100

print(f"Volume of Sphere A: {volume_A} cubic gigaparsecs")
print(f"Volume of Sphere B: {volume_B} cubic gigaparsecs")
print(f"Percentage of B compared to A: {percentage_B_to_A:.2f}%")
```
