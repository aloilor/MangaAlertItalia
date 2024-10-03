import sys
import os

# Get the absolute path to the 'backend' directory
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

# Add 'backend' to sys.path so all packages inside it are discoverable
sys.path.insert(0, backend_path)
