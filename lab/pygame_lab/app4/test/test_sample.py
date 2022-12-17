# -*- coding: utf-8 -*-
#!/usr/bin/python3
"""
@package: test_sample.py

Learning to use pytest

Execute "pytest" from command line.
It will execute all python scripts named like "test_*.py" or "*_test.py"

It fails with a bizarre error: 'Function' object has no attribute 'get_marker'
Tried doing the suggested updates. No luck.
Not naming the test function like "test_*" prevents the error, but also prevents it from picking up the test.

So... not using pytest for now!
"""
def func(x):
    return x + 1

def test_func():
    assert func(3) == 5
