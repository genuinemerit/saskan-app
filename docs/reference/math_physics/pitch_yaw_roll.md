# Pitch Yaw and Roll

Rolling, rotating, and reorienting a 3D ellipsoid (or any 3D object) involves a concept similar to the aviation terms of "pitch," "yaw," and "roll," but the terminology may vary in different contexts. Here's how you can express these rotations and what units are commonly used:

1. **Pitch**: Pitch rotation typically refers to the rotation around the horizontal (X) axis. In aviation, this is commonly associated with tilting the nose of an aircraft up or down. The unit of measure can be degrees or radians. Both degrees and radians are widely used, and the choice often depends on the specific application or library you're using. In Python, libraries like NumPy and most 3D libraries support rotations in both degrees and radians.

2. **Yaw**: Yaw rotation involves the rotation around the vertical (Y) axis. This is like turning left or right. Again, degrees or radians can be used for measurement.

3. **Roll**: Roll rotation is around the depth (Z) axis. This is similar to tilting to the side. Degrees or radians can be used here as well.

The choice of degrees or radians depends on the library or framework you're using and your personal preference. Radians are often preferred in mathematical and computational contexts due to their mathematical properties, but degrees are more commonly used in everyday discussions.

In terms of expressing these rotations in 3D, you typically use rotation matrices or quaternions to represent the orientation of the ellipsoid after rotation. The specific mathematics and notation may vary depending on the libraries you're using. For example, in Python, libraries like NumPy provide functions for performing 3D rotations.

Here's a general idea of how you might perform these rotations:

* Pitch (X-axis rotation):

  ```python
  from scipy.spatial.transform import Rotation as R
  r = R.from_euler('x', angle, degrees=True)  # Rotate by 'angle' degrees around X-axis
  new_orientation = r.apply(original_orientation)
  ```

* Yaw (Y-axis rotation):

  ```python
  r = R.from_euler('y', angle, degrees=True)  # Rotate by 'angle' degrees around Y-axis
  new_orientation = r.apply(original_orientation)
  ```

* Roll (Z-axis rotation):

  ```python
  r = R.from_euler('z', angle, degrees=True)  # Rotate by 'angle' degrees around Z-axis
  new_orientation = r.apply(original_orientation)
  ```

The key is to use a library that provides these rotation functions and to be consistent with your choice of degrees or radians for the rotation angles.

---

## Direction of Rotation

The direction of rotation, whether it's "up" or "down," "left" or "right," is expressed through the sign (positive or negative) of the rotation angle. The convention for specifying the direction of rotation around an axis, such as pitch, yaw, or roll, is as follows:

1. Positive rotation: This corresponds to rotating in the "counter-clockwise" or "anticlockwise" direction when viewing the rotation axis from the positive end. For example, if you're looking along the positive X-axis and you want to pitch "up," you'd use a positive angle.

2. Negative rotation: This corresponds to rotating in the "clockwise" direction when viewing the rotation axis from the positive end. If you want to pitch "down," you'd use a negative angle.

The choice of the sign (positive or negative) depends on your coordinate system and the specific library or mathematical convention you're following. In many standard 3D libraries and systems, the positive direction for pitch, yaw, and roll follows the "right-hand rule," which is a widely accepted convention in mathematics and physics.

* In the right-hand rule, when you point your right thumb in the positive direction of the rotation axis (e.g., the X-axis for pitch), the fingers of your right hand curl in the positive (counter-clockwise) direction of rotation.

* For pitch, positive rotation tilts "up" when looking along the positive X-axis (right thumb points in the direction of positive X-axis).

* For yaw, positive rotation turns to the "right" when looking along the positive Y-axis (right thumb points in the direction of positive Y-axis).

* For roll, positive rotation tilts to the "right" when looking along the positive Z-axis (right thumb points in the direction of positive Z-axis).

It's essential to maintain consistency in the sign of rotation angles to correctly specify the desired direction of rotation in your specific system or library.
