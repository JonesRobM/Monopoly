"""
Utility to suppress common NumPy warnings on Windows.

Add this to the top of your scripts if you encounter NumPy MINGW-W64 warnings.
"""

import warnings
import os

# Suppress NumPy MINGW-W64 warnings on Windows
warnings.filterwarnings("ignore", message=".*MINGW-W64.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="numpy")

# Alternative: Set environment variable (do this before importing numpy)
os.environ.setdefault('PYTHONWARNINGS', 'ignore::RuntimeWarning')
