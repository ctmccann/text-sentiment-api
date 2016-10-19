import os
import sys

curr_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, curr_dir)

from app import app as application
