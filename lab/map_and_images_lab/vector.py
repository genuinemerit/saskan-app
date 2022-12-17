#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Examples and explanations of vector operations, using NumPy.

:module: vector.py
:author: dave <genuinemerit at pm.me>
:modified: Wed Feb 18 2021

:class:  Vector

See: https://www.britannica.com/science/vector-physics

Demonstrate using numpy to define vector structures used in physics.
See the book: Physics for Game Developers, esp. appendices on Vector
Operations and Quaternions.

NumPy and SciPy already have these operations covered.
This is a pedagogical exercise to explore certain concepts.
Along with learning basic vector operations and terminology,
interesting python lessons include:

- Magic methods on classes and functions which return metadata.
- Operation overrides. Much awesome.

Operator overides are quite interesting.
See https://docs.python.org/2/reference/datamodel.html and keep scrolling.
This class provide overrides for emulating various mathematical operations
against instances of the class. That means we can do vector operations
using math operators like +, -, *, etc.
"""

from math import sqrt
from pprint import pprint as pp

import numpy as np


class Vector:
    """Define basic components of a Vector structure."""

    def __init__(self):
        """Instantiate Vector object."""
        # vector components
        self.x = np.float_()
        self.y = np.float_()
        self.z = np.float_()
        # normalized vector components
        self.Nx = np.float_()
        self.Ny = np.float_()
        self.Nz = np.float_()
        # reversed vector components
        self.Rx = np.float_()
        self.Ry = np.float_()
        self.Rz = np.float_()
        # derived vector components
        self.Dx = np.float_()
        self.Dy = np.float_()
        self.Dz = np.float_()
        # scalar values
        self.magnitude_val = np.float_()
        self.cross_val = np.float_()
        self.dot_product_val = np.float_()
        self.triple_val = np.float_()

        self.reset_vector()

    def reset_vector(self):
        """Initialize Vector attributes."""
        self.x = np.float_(0)
        self.y = np.float_(0)
        self.z = np.float_(0)
        self.Nx = np.float_(0)
        self.Ny = np.float_(0)
        self.Nz = np.float_(0)
        self.Rx = np.float_(0)
        self.Ry = np.float_(0)
        self.Rz = np.float_(0)
        self.Dx = np.float_(0)
        self.Dy = np.float_(0)
        self.Dz = np.float_(0)
        self.magnitude_val = np.float_(0)
        self.cross_val = np.float_(0)
        self.dot_product_val = np.float_(0)
        self.triple_val = np.float_(0)

    def set_components(self, xi: float, yi: float, zi: float) -> tuple:
        """Set Vector attributes from input.

        Args:
            xi (float): x-value of component
            yi (float): y-value of component
            zi (float): z-value of component
        Returns:
            tuple: (x, y, z) cast to NumPy floats
        """
        self.x = np.float_(xi)
        self.y = np.float_(yi)
        self.z = np.float_(zi)
        return (self.x, self.z, self.y)

    def magnitude(self) -> float:
        """Magnitude basically means length.

        Calculate scalar magnitude of vector according to formula:
            |v| = sqrt(x**2 + y**2 + z**2)
        For a zero-based vector where components are specified
        relative to origin.

        Returns:
            numpy float: Magnitude of vector(x, y, z)
        """
        self.magnitude_val = np.float_(sqrt(self.x**2 + self.y**2 + self.z**2))
        return self.magnitude_val

    def normalize(self, change_components: bool = False) -> tuple:
        """Convert the vector to a unit vector.

        Satisfy the equation:
            |v| = sqrt(x**2 + y**2 + z**2) = 1
        In other words, assume the length of the normalized vector is 1 unit.
        If v is a non-unit vector with components x, y, z, then calculate
        the unit vector u as follows:
            u = v / |v| = (x / |v|) I + (y / |v|) j + (z / |v|) k
            where |v| is the magnitude.
        Store result in this objects's normalized component values.
        If change_components is True, then also overlay the base components.

        For an explanation, see: https://en.wikipedia.org/wiki/Unit_vector

        Args:
            change_components (bool): overlay the vector components
        Returns:
            tuple (x, y, z) of normalized vector components
        """
        TOL = np.float_(0.00001)
        self.magnitude()
        if (self.magnitude_val <= TOL):
            self.magnitude_val = 1.0
        self.Nx = self.x / self.magnitude_val
        self.Ny = self.y / self.magnitude_val
        self.Nz = self.z / self.magnitude_val
        if (abs(self.Nx) < TOL):
            self.Nx = 0.0
        if (abs(self.Ny) < TOL):
            self.Ny = 0.0
        if (abs(self.Nz) < TOL):
            self.Nz = 0.0
        if change_components:
            self.set_components(self.Nx, self.Ny, self.Nz)
        return (self.Nx, self.Ny, self.Nz)

    def reverse(self, change_components: bool = False) -> tuple:
        """Reverse direction of the vector.

        Take the negative of each component. Vector will point opposite
        to where it pointed previously.
        Store result in this objects's reversed component values.
        If change_components is True, then also overlay the base components.

        Args:
            change_components (bool): overlay the vector components
        Returns:
            tuple (x, y, z) of reversed vector components
        """
        self.Rx = -(self.x)
        self.Ry = -(self.y)
        self.Rz = -(self.z)
        if change_components:
            self.set_components(self.Rx, self.Ry, self.Rz)
        return (self.Rx, self.Ry, self.Rz)

    def __add__(self, other: object) -> tuple:
        """Add an other Vector to this Vector.

        + operator

        Add component by component. Produce a new vector.
        Don't change existing vector's based (x,y,z) components.
        Store result in the object's derived component values.

        Args:
            other (Vector): a Vector object
        Returns:
            tuple: (x, y, z) of resulting added vector components
        """
        self.Dx = self.x + other.x
        self.Dy = self.y + other.y
        self.Dz = self.z + other.z
        return (self.Dx, self.Dy, self.Dz)

    def __iadd__(self, other: object) -> object:
        """Add an other Vector and modify this Vector.

        += operator

        Args:
            other (Vector): a Vector object
        Returns:
            object: the modified vector object

        This operation is a little confusing. It works, but only
        if I return the entire object, after rebuilding it using
        the results of the process.
        If I return only the modified or original components, then
        the entire object gets replaced by a simple tuple.

        Also, this operator does not seem to get recognized if
        used inside of a print() or pp() statement.
        """
        self + other
        T = Vector()
        T.set_components(self.Dx, self.Dy, self.Dz)
        self = T
        return self

    def __sub__(self, other: object) -> tuple:
        """Subtract passed vector, component by component.

        - operator

        Produce a new vector.
        Don't change existing vector's based (x,y,z) components.
        Store result in the object's derived component values.

        Args:
            other (Vector): a Vector object
        Returns:
            tuple: (x, y, z) of resulting subtracted vector components
        """
        self.Dx = self.x - other.x
        self.Dy = self.y - other.y
        self.Dz = self.z - other.z
        return (self.Dx, self.Dy, self.Dz)

    def __mul__(self, scalar: float) -> tuple:
        """Multiply vector by a scalar.

        * operator

        Scale the length of the vector.

        Produce a new vector.
        Don't change existing vector's based (x,y,z) components.
        Store result in the object's derived component values.

        Args:
            scalar (number): a scalar value
        Returns:
            tuple: (x, y, z) of resulting multiplied vector components
        """
        mult = np.float_(scalar)
        self.Dx = self.x * mult
        self.Dy = self.y * mult
        self.Dz = self.z * mult
        return (self.Dx, self.Dy, self.Dz)

    def __truediv__(self, scalar: float) -> tuple:
        """Divide vector by scalar.

        / operator

        Scale the length of the vector.

        Produce a new vector.
        Don't change existing vector's based (x,y,z) components.
        Store result in the object's derived component values.

        Args:
            scalar (number): a scalar value
        Returns:
            tuple: (x, y, z) of resulting divided vector components
        """
        divi = np.float_(scalar)
        self.Dx = self.x / divi
        self.Dy = self.y / divi
        self.Dz = self.z / divi
        return (self.Dx, self.Dy, self.Dz)

    def __floordiv__(self, scalar: float) -> tuple:
        """Divide vector by scalar.

        // operator

        Scale the length of the vector, using "floor" division.

        Produce a new vector.
        Don't change existing vector's based (x,y,z) components.
        Store result in the object's derived component values.

        Args:
            scalar (number): a scalar value
        Returns:
            tuple: (x, y, z) of resulting divided vector components
        """
        divi = np.float_(scalar)
        self.Dx = self.x // divi
        self.Dy = self.y // divi
        self.Dz = self.z // divi
        return (self.Dx, self.Dy, self.Dz)

    def __neg__(self) -> tuple:
        """Unary negation of a vector is same as a reverse.

        unary - operator

        Change the base vector components when this operator is used.

        Returns:
            tuple (x, y, z) of reversed vector components
        """
        return self.reverse(True)

    def __pow__(self, other: object) -> float:
        """Apply the Vector Cross Product.

        ** operator

        The power operator returns a vector perpendicular to
        self (o) and other (v).
        In written formulas, this operation is represented as X.
        It is computed as:
            (oy * vz - oz * vy),  (-ox * vz + oz * vx),  (ox * vy - oy * vx)
        If the vectors are parallel, their cross-product is zero.

        Cross Product is also referred to as the normal vector.
        Useful in collision detection, to find vector normal to the
        face of a polygon.

        For some calculation, we're interested in the vector result.
        In others the scalar result which is the sum of the vector components
        is more useful for physics. Here we return that scalar sum of the
        cross product result.

        Args:
            other (Vector): a Vector object
        Returns:
            scalar: sum of resulting cross-multiplied vector components
        """
        self.Dx = (other.y * self.z) - (other.z * self.y)
        self.Dy = (-(other.x) * self.z) + (other.z * self.x)
        self.Dz = (other.x * self.y) - (other.y * self.x)
        self.cross_val = self.Dx + self.Dy + self.Dz
        return self.cross_val

    def dot(self, other: object) -> float:
        """Compute dot product of two vectors.

        ⋅ operator

        UTF dot operator character:
        https://www.utf8icons.com/character/8901/dot-operator
        U+22C5
        Part of the mathematical operators Unicode sub-set:
        https://www.utf8icons.com/subsets/mathematical-operators

        Return a scalar used to calculate length of segment of (v) that is
        "covered" by other vector (o), when both are assumed to have a
        zero (0,0,0) origin.  This the 'projection' of vector o onto vector v.

        In written formulas, this operation is represented using the dot
        character •  There is no natural equivalent in python so we just use a
        regular function definition instead of an operator override.

        FYI, tried defining a function just named "⋅" (U+22C5) but python
        would not accept on oddball Unicode character as a function name.

        Args:
            other (Vector): a Vector object
        Returns:
            scalar: sum of resulting cross-multiplied vector components
        """
        self.dot_product_val = ((self.x * other.x) +
                                (self.y * other.y) +
                                (self.z * other.z))
        return self.dot_product_val

    def triple(self, other: object, another: object) -> float:
        """Compute a Triple Scalar Product.

        The triple Scalar Product of three vectors (v, o, w) is computed as:
            S = o • (v X w)
        Take the cross product of v and w, then against the result
        apply the dot product of o.

        Args:
            other (Vector): a Vector object
            another (Vector): a Vector object
        Returns:
            scalar: sum of resulting triple scalar product
        """
        self ** another
        o = Vector()
        o.set_components(self.Dx, self.Dy, self.Dz)
        self.triple_val = other.dot(o)
        return self.triple_val


def run():
    """Display results to help understand Vector structures."""

    def show_object():
        """Display initialized object features.

        Learn about magic qualities of classes.
        Extra credit -- read up on __repr__.
        """
        print("\n==== Object =====\n")
        pp(("V = Vector()", V))
        pp(("V.dict", V.__class__.__dict__))
        pp(("V.doc", V.__class__.__doc__))
        pp(("V.module", V.__class__.__module__))
        pp(("V.name", V.__class__.__name__))

    def show_methods():
        """Display Vector methods and attributes.

        Examples of:
        - magic __default__ value of methods
        - component set up
        - magnitude method and attribute
        - normalize, compute only
        - normalize and change base components
        - reverse, compute only
        - reverse and change base components
        """
        print("\n==== Methods =====\n")

        pp(("V.set_components.__defaults__",
            V.set_components.__defaults__))
        pp(("V.set_components(14.23, -60, 239.2)",
            V.set_components(14.23, -60, 239.2)))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))

        print("\n")
        pp(("V.magnitude (before)", V.magnitude))
        pp(("V.magnitude.__defaults__",
            V.magnitude.__defaults__))
        pp(("V.magnitude()", V.magnitude()))
        pp(("V.magnitude (after)", V.magnitude))

        print("\n")
        pp(("V.normalize.__defaults__",
            V.normalize.__defaults__))
        pp(("V.normalize() <-- use default", V.normalize()))
        pp(("V.Nx, V.Ny, V.Nz", V.Nx, V.Ny, V.Nz))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.normalize(change_components = True)",
            V.normalize(change_components=True)))
        pp(("V.Nx, V.Ny, V.Nz", V.Nx, V.Ny, V.Nz))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))

        print("\n")
        pp(("V.reverse.__defaults__",
            V.reverse.__defaults__))
        pp(("V.reverse() <-- use default", V.reverse()))
        pp(("V.Rx, V.Ry, V.Rz", V.Rx, V.Ry, V.Rz))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.reverse(change_components = True)",
            V.reverse(change_components=True)))
        pp(("V.Rx, V.Ry, V.Rz", V.Rx, V.Ry, V.Rz))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))

    def show_operations():
        """Display Vector operator overrides.

        Examples of:
        - add  +
        - iadd +=
        - sub  -
        - mult *
        - div /
        - negate !
        - power/cross-product **
        - dot
        - triple
        """
        print("\n==== Operator Overrides =====\n")
        V = Vector()
        pp(("V.set_components(14, -60, 27)",
           V.set_components(14, -60, 27)))
        O = Vector()        # noqa E741
        pp(("O.set_components(10, -2, 57)",
           O.set_components(10, -2, 57)))

        print("\n{}".format(V.__class__.__add__.__doc__))
        pp(("V + O", V + O))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("O.x, O.y, O.z", O.x, O.y, O.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))
        pp(("O.Dx, O.Dy, O.Dz", O.Dx, O.Dy, O.Dz))

        print("\n{}".format(V.__class__.__iadd__.__doc__))
        pp(("Before.. V.x, V.y, V.z", V.x, V.y, V.z))
        print("(V + O, ")
        V += O
        print(")")
        pp(("After.. V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("O.x, O.y, O.z", O.x, O.y, O.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))
        pp(("O.Dx, O.Dy, O.Dz", O.Dx, O.Dy, O.Dz))

        print("\n{}".format(V.__class__.__sub__.__doc__))
        pp(("V - O", V - O))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("O.x, O.y, O.z", O.x, O.y, O.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))
        pp(("O.Dx, O.Dy, O.Dz", O.Dx, O.Dy, O.Dz))

        print("\n{}".format(V.__class__.__mul__.__doc__))
        pp(("V * 4", V * 4))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))
        pp(("V * 0.4", V * 0.4))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))

        print("\n{}".format(V.__class__.__truediv__.__doc__))
        pp(("V / 2.3", V / 2.3))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))

        print("\n{}".format(V.__class__.__floordiv__.__doc__))
        pp(("V // 2.3", V // 2.3))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))

        print("\n{}".format(V.__class__.__neg__.__doc__))
        pp(("Before... V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("-V", -V))
        pp(("After... V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.Rx, V.Ry, V.Rz", V.Rx, V.Ry, V.Rz))

        print("\n{}".format(V.__class__.__pow__.__doc__))
        pp(("V ** O", V ** O))
        pp(("V.cross_val", V.cross_val))
        pp(("V.x, V.y, V.z", V.x, V.y, V.z))
        pp(("V.Dx, V.Dy, V.Dz", V.Dx, V.Dy, V.Dz))

        print("\n{}".format(V.__class__.dot.__doc__))
        V = Vector()
        V.set_components(14, -60, 27)
        O = Vector()        # noqa E741
        O.set_components(10, -2, 57)
        pp(("V.x, V.y, V.z before...", V.x, V.y, V.z))
        pp(("O.x, O.y, O.z before...", O.x, O.y, O.z))
        pp(("V.dot(O)", V.dot(O)))
        pp(("V.dot_product_val", V.dot_product_val))
        pp(("V.x, V.y, V.z after...", V.x, V.y, V.z))
        pp(("V.Dx, V.Dy, V.Dz after...", V.Dx, V.Dy, V.Dz))
        pp(("O.x, O.y, O.z after...", O.x, O.y, O.z))

        print("\n{}".format(V.__class__.triple.__doc__))
        V = Vector()
        V.set_components(14, -60, 27)
        O = Vector()        # noqa E741
        O.set_components(10, -2, 57)
        W = Vector()
        W.set_components(-5, 7, -3)
        pp(("V.x, V.y, V.z before...", V.x, V.y, V.z))
        pp(("O.x, O.y, O.z before...", O.x, O.y, O.z))
        pp(("W.x, W.y, W.z before...", W.x, W.y, W.z))
        pp(("V.triple(O, W)", V.triple(O, W)))
        pp(("V.triple_val", V.triple_val))
        pp(("V.x, V.y, V.z after...", V.x, V.y, V.z))
        pp(("V.Dx, V.Dy, V.Dz after...", V.Dx, V.Dy, V.Dz))
        pp(("O.x, O.y, O.z after...", O.x, O.y, O.z))
        pp(("W.x, W.y, W.z after...", W.x, W.y, W.z))

    V = Vector()
    show_object()
    show_methods()
    show_operations()

    """
    w = Vector()
    w.set_components(-7.2, 21, 43)
    print "x:", w.x, "y:", w.y, "z:", w.z
    print "\ntriple Product of v, o, w:\n==========="
    print v.__class__.triple.__doc__
    print v.triple(o, w)
    """


if __name__ == '__main__':
    run()
