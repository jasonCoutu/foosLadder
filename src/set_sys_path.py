"""Sets sys.path for the library directories."""

import os
import sys

current_path = os.path.abspath(os.path.dirname(__file__))

def set_sys_path():
    # Add lib as primary libraries directory, with fallback to lib/dist
    # and optionally to lib/dist.zip, loaded using zipimport.
    sys.path[0:0] = [
        os.path.join(current_path, 'lib'),
    ]

set_sys_path()
