import sys
import os

# Print Python version and path info
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print("Python path:")
for p in sys.path:
    print(f"  {p}")

# Check if there's any PYTHONSTARTUP file
startup_file = os.environ.get('PYTHONSTARTUP')
print(f"PYTHONSTARTUP: {startup_file}")

print("Done") 