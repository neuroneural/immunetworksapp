import os
import platform
import subprocess
import sys


def create_virtualenv():
    """Create a virtual environment using appropriate method based on OS."""
    venv_dir = "venv"
    if not os.path.exists(venv_dir):
        if platform.system() == "Windows":
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        else:
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

def install_requirements():
    """Install requirements from requirements.txt."""
    subprocess.check_call([os.path.join("venv", "bin" if not platform.system() == "Windows" else "Scripts", "pip"),
                           "install", "-r", "requirements.txt"])

def main():
    print("Creating virtual environment...")
    create_virtualenv()

    print("Installing requirements...")
    install_requirements()

    print("Building the executable...")
    subprocess.check_call([os.path.join("venv", "bin" if not platform.system() == "Windows" else "Scripts", "pyinstaller"),
                           "--onefile",
                           "--add-data", "resources:resources",
                           "--add-data", "appresources:appresources",
                           "app.py"])

if __name__ == "__main__":
    main()
