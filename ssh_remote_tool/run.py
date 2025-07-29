#!/usr/bin/env python3
"""
SSH Remote Operations Tool - Launcher Script
"""
import sys
import os

# Add the src directory to the path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Change to src directory to ensure relative paths work correctly
os.chdir(src_path)

from main import main

if __name__ == "__main__":
    sys.exit(main())
