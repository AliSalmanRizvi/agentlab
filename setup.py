#!/usr/bin/env python3
"""
Setup script for AWS configuration
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the setup
from setup_aws import main

if __name__ == "__main__":
    main()