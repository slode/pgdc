import os, sys

here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, here)

if 'profile' not in globals():
    def profile(func):
        return func
