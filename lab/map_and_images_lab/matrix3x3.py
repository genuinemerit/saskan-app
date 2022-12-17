#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
This lesson continues basic exploration of numpy and basic structures used in physics.
 The book Physics for Game Developers, particularly the appendices on Vector Operations,
 Matrix Operations and Quaternions, was used as source for these lessons.
 This lesson provides a Matrix3X3 class, along with examples and explanations
 of its Operations.

 Much of this can probaby be accomplished with existing NumPy and SciPy structures.
 The point of re-creating it here is mainly autodidactic pedagogy... yeah,
 teachin' meself this stuff here...

"""
import math, cmath
import numpy as np
import sys

class Matrix3x3:
    '''
    A Matrix 3X3 class is defined with 9 elements, described as e(ij),
    where the ij is subscripted in written formulas.  i represents the
    i-th row j the j-th column.  So for example  e(21) refers to 1st
    element on the 2nd row. Basically it an array of three 3-tuples.
    '''
    def __init__(self):
        '''
        Instantiate Matrix3x3 object.
        '''
        i = np.array([np.float_(), np.float_(), np.float_() ])
        # the Matrix
        self.mx = np.array([i, i, i])
        # Modified Matrix
        self.dmx = np.array([i, i, i])
        # Determinant
        self.det = np.float_()

        self.ResetMatrix()

    def ResetMatrix(self):
        '''
        Initialize Matrix3x3 attributes
        '''
        for i in range(0,2):
            for j in range(0,2):
                self.mx[i,j]=0.0
                self.dmx[i,j]=0.0

        self.det = 0.0

        return self.mx

    def SetMatrix(self, mvals):
        '''
        Set the matrix values to those passed in as parameters.
        We assume mvals is a valid 2D, 3X3 array.

        Some python lessons here:
        1) Multi-indexing on ndarray's works, but not on lists of lists.
           A list only ever takes a single integer index, so we have
           break out our regular list-y array in order to apply an index
           to the interior list. But for our ndarray, we can use multi-indexes.
        2) Remember: range includes the first value, but the second value
           defines the "less than" limit, not the maximum value.
        '''
        self.ResetMatrix()

        for i in range(0,3):
            for j in range(0,3):
                mrow = mvals[i]
                self.mx[i,j]=mrow[j]

        return self.mx

    def __setChangedMatrix(self):
        '''
        Private. 
        
        Convert dmx to a regular list of lists and use it as input
        to the SetMatrix method.
        
        Ho-ho, boys and girls...  It's python lesson time! 
        What Python does not have at all is PROTECTED methods.  
        A PRIVATE method in Python is identified solely by its NAME.  
        If it starts (but does not end) with two underbars, then it is private. 
        '''
        drow = [0.0, 0.0, 0.0]
        dm = [drow, drow, drow]
        dm = [[self.dmx[0,0], self.dmx[0,1], self.dmx[0,2]], \
              [self.dmx[1,0], self.dmx[1,1], self.dmx[1,2]], \
              [self.dmx[2,0], self.dmx[2,1], self.dmx[2,2]]]
        return self.SetMatrix(dm)
        
    def Determinant(self):
        '''
        Set the determinant of the matrix. A determinant is computed on a 2x2 matrix.
        It is computed as:
            e(11)*e(22) - e(21)*e(12)
        To compute the overall determinant of a 3X3 matrix:
            Expand the 3X3 matrix into "minors" and compute the determinant of each.
            Subtract the second from the first. Add the third one.
        Or to put it in terms of all the e-values:
            e11*e22*e33 -
            e11*e32*e23 +
            e21*e32*e13 -
            e21*e12*e33 +
            e31*e12*e23 -
            e31*e22*e13
        '''
        self.det = (self.mx[0,0] * self.mx[1,1] * self.mx[2,2]) -   \
                   (self.mx[0,0] * self.mx[2,1] * self.mx[1,2]) +   \
                   (self.mx[1,0] * self.mx[2,1] * self.mx[0,2]) -   \
                   (self.mx[1,0] * self.mx[0,1] * self.mx[2,2]) +   \
                   (self.mx[2,0] * self.mx[0,1] * self.mx[1,2]) -   \
                   (self.mx[2,0] * self.mx[1,1] * self.mx[0,2])
        return self.det

    def Transpose(self):
        '''
        Transpose the matrix by swapping rows with columns.  Elements of the
        first row become elements in the first column and so on.
        It is kind of (but not exactly) like rotating the matrix.
        '''
        tmx = [[self.mx[0,0], self.mx[1,0], self.mx[2,0]], \
               [self.mx[0,1], self.mx[1,1], self.mx[2,1]], \
               [self.mx[0,2], self.mx[1,2], self.mx[2,2]] ]
        self.SetMatrix(tmx)
        return self.mx

    def Inverse(self, change_matrix=False):
        '''
        To find the inverse M(-1) of a 3x3 matrix (M), apply a value 1/det(M) to M.
        Only square matrices -- those with an equal number of rows and columns --
        can be inverted, but not all square matrices can be inverted. It can be
        inverted only if its determinant in nonzero.

        This function is set up so that we can compute the Inverse without
        changing the matrix.  If change_matrix is set to True, then we also
        modify the matrix.

        I don't quite understand what this is doing, but... whatever...
        '''
        d = self.Determinant()
        if (d == 0.0):
            d = 1.0

        drow = [0.0, 0.0, 0.0]
        dm = [drow, drow, drow]

        drow[0] = (self.mx[1,1] * self.mx[2,2] -
                   self.mx[1,2] * self.mx[2,1]) / d
        drow[1] = -(self.mx[0,1] * self.mx[2,2] -
                    self.mx[0,2] * self.mx[2,1]) / d
        drow[2] = (self.mx[0,1] * self.mx[1,2] -
                   self.mx[0,2] * self.mx[1,1]) / d
        dm[0] = drow

        drow[0] = -(self.mx[1,0] * self.mx[2,2] -
                    self.mx[1,2] * self.mx[2,0]) / d
        drow[1] = (self.mx[0,0] * self.mx[2,2] -
                   self.mx[0,2] * self.mx[2,0]) / d
        drow[2] = -(self.mx[0,0] * self.mx[1,2] -
                    self.mx[0,2] * self.mx[1,0]) / d
        dm[1] = drow

        drow[0] = (self.mx[1,0] * self.mx[2,1] -
                   self.mx[1,1] * self.mx[2,0]) / d
        drow[1] = -(self.mx[0,0] * self.mx[2,1] -
                    self.mx[0,1] * self.mx[2,0]) / d
        drow[2] = (self.mx[0,0] * self.mx[1,1] -
                   self.mx[0,1] * self.mx[1,0]) / d
        dm[2] = drow

        for i in range(0,3):
            drow = dm[i]
            for j in range(0,3):
                self.dmx[i,j] = drow[j]

        if change_matrix:
            self.SetMatrix(dm)
        return self.dmx

    def __add__(self, o):
        '''
        Add all elements in other Matrix to current Matrix.
        Obviously, the two matrices must be of the same order -- that is,
        have the same number of rows and columns
        '''
        for i in range(0,3):
            for j in range(0,3):
                self.dmx[i,j] = self.mx[i,j] + o.mx[i,j]
        return self.dmx

    def __sub__(self, o):
        '''
        Subtract all elements in other Matrix from current Matrix.
        The two matrices must be of the same order.
        '''
        for i in range(0,3):
            for j in range(0,3):
                self.dmx[i,j] = self.mx[i,j] - o.mx[i,j]
        return self.dmx

    def __mul__(self, multi):
        '''
        Scalar Multiply operation against the Matrix.
        Multiply all elements in current Matrix by the scalar value.
        '''
        for i in range(0,3):
            for j in range(0,3):
                self.dmx[i,j] = self.mx[i,j] * multi
        return self.dmx

    def __div__(self, divi):
        '''
        Scalar Divide operation against the Matrix.
        Divide all elements in current Matrix by the scalar value.
        '''
        for i in range(0,3):
            for j in range(0,3):
                self.dmx[i,j] = self.mx[i,j] / divi
        return self.dmx

    def __truediv__(self, divi):
        '''
        Divide all elements in current Matrix by the scalar value.
        Same as __div__
        '''
        return self.__div__(divi)

    def MultVector(self, vector, change_matrix=False):
        '''
        Vector Multiplication against a Matrix multiplies the i-th
        column of the matrix by the i-th component in the vector.

        So x is multiplied against the first column in each row,
           y is multiplied against the second column in each row,
           z is multiplied against the third column in each row.

        Provide option to update the Matrix.
        '''
        for i in range(0,3):
            for j in range(0,3):
                self.dmx[i,j] = self.mx[i,j] * vector[i]
                
        if change_matrix:
            self.__setChangedMatrix()

        return self.dmx

    def MultMatrix(self, o, change_matrix=False):
        '''
        Matrix Multiplication against a Matrix multiplies the i-th
        column of the first matrix by the j-th element of the second matrix.
        This can be captured as single combination of multiplies and adds
        for each derived row.

        Provide option to update the Matrix.
        '''
        self.dmx[0,0] = self.mx[0,0]*o.mx[0,0] + self.mx[0,1]*o.mx[1,0] + self.mx[0,2]*o.mx[2,0]
        self.dmx[0,1] = self.mx[0,0]*o.mx[0,1] + self.mx[0,1]*o.mx[1,1] + self.mx[0,2]*o.mx[2,1]
        self.dmx[0,2] = self.mx[0,0]*o.mx[0,2] + self.mx[0,1]*o.mx[1,2] + self.mx[0,2]*o.mx[2,2]
        
        self.dmx[1,0] = self.mx[1,0]*o.mx[0,0] + self.mx[1,1]*o.mx[1,0] + self.mx[1,2]*o.mx[2,0]
        self.dmx[1,1] = self.mx[1,0]*o.mx[0,1] + self.mx[1,1]*o.mx[1,1] + self.mx[1,2]*o.mx[2,1]
        self.dmx[1,2] = self.mx[1,0]*o.mx[0,2] + self.mx[1,1]*o.mx[1,2] + self.mx[1,2]*o.mx[2,2]
        
        self.dmx[2,0] = self.mx[2,0]*o.mx[0,0] + self.mx[2,1]*o.mx[1,0] + self.mx[2,2]*o.mx[2,0]
        self.dmx[2,1] = self.mx[2,0]*o.mx[0,1] + self.mx[2,1]*o.mx[1,1] + self.mx[2,2]*o.mx[2,1]
        self.dmx[2,2] = self.mx[2,0]*o.mx[0,2] + self.mx[2,1]*o.mx[1,2] + self.mx[2,2]*o.mx[2,2]
                
        if change_matrix:
            self.__setChangedMatrix()

        return self.dmx

def main():
    print '\nClass Matrix3x3:\n============'
    m = Matrix3x3()
    print m.__class__.__dict__
    print m.__class__.__doc__
    print '\nSetMatrix:\n============'
    print m.SetMatrix.__doc__
    print m.SetMatrix([[12,2,31],[6,19.2,-33],[45,3.141,0.75464324]])
    print '\nDeterminant:\n============'
    print m.Determinant.__doc__
    print m.Determinant()
    print '\nTranspose:\n============'
    print m.Transpose.__doc__
    print m.Transpose()
    print '\nInverse:\n============'
    print m.Inverse.__doc__
    print m.Inverse()
    print m.mx
    print '\nInverse with save:\n============'
    print m.Inverse(True)
    print m.mx
    print '\nSet up Matrix u:\n============'
    u = Matrix3x3()
    print u.SetMatrix([[1,2,3],[5,8,13],[21,34,55]])
    print '\nAdd u to m:\n============'
    print m.__add__.__doc__
    print m + u
    print '\nSubtract u from m:\n============'
    print m.__sub__.__doc__
    print m - u
    print '\nMultiply m by a scalar value (5):\n============'
    print m.__mul__.__doc__
    print m * 5
    print '\nDivde m by a scalar value (3):\n============'
    print m.__div__.__name__
    print m.__div__.__doc__
    print m.__truediv__.__name__
    print m.__truediv__.__doc__
    print m / 3
    print '\nVector Multiply m by v:\n============'
    v = [34, 27, 18]
    print v
    print m.MultVector.__doc__
    print m.MultVector(v)
    print m.mx
    print '\nVector Multiply m by v, with save:\n============'
    print m.MultVector(v, True)
    print m.mx
    print '\nMatrix Multiply m by u:\n============'
    print m.MultMatrix.__doc__
    print m.MultMatrix(u)
    print m.mx
    print '\nMatrix Multiply m by u, with save:\n============'
    print m.MultMatrix(u, True)
    print m.mx

if __name__ == '__main__':
    main()
