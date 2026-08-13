import os
import sys

backend_dir = os.path.dirname(os.path.abspath(__file__))
venv_lib = os.path.join(backend_dir, "venv", "Lib", "site-packages", "torch", "lib")

print(f"Checking torch lib dir: {venv_lib}")
if os.path.exists(venv_lib):
    print("Files in torch/lib:")
    files = os.listdir(venv_lib)
    for f in files[:15]:
        print(" ", f)

# Try adding torch/lib to DLL directory (Python 3.8+ on Windows requires os.add_dll_directory)
if hasattr(os, "add_dll_directory") and os.path.exists(venv_lib):
    try:
        os.add_dll_directory(venv_lib)
        print("\nAdded torch/lib to os.add_dll_directory!")
    except Exception as e:
        print("add_dll_directory error:", e)

# Now try importing torch
try:
    import torch
    print("\nSUCCESS: torch imported successfully!")
    print(f"torch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
except Exception as e:
    print("\nFAILED to import torch:")
    print(e)
    import traceback
    traceback.print_exc()
