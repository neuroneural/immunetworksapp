#!/bin/bash

# Function to check if the OS is macOS
check_macos() {
    if [ $(uname) == "Darwin" ]; then
        echo "macOS detected."
        return 0
    else
        echo "This is not macOS."
        return 1
    fi
}

# Function to check if the OS is Debian-based (e.g., Ubuntu)
check_debian() {
    if [ -f /etc/debian_version ] || [ -f /etc/lsb-release ]; then
        echo "Debian-based Linux detected."
        return 0
    else
        echo "This is not a Debian-based Linux distribution."
        return 1
    fi
}

# Function to check if the OS is Red Hat-based (e.g., CentOS, Fedora)
check_redhat() {
    if [[ -f /etc/redhat-release ]]; then
        echo "Red Hat-based Linux detected."
        return 0
    else
        echo "This is not a Red Hat-based Linux distribution."
        return 1
    fi
}

# Function to check if Python 3 exists, and install if necessary (macOS)
check_python_macos() {
    if command -v python3 &>/dev/null; then
        echo "Python 3 is already installed."
        return 0
    else
        echo "Python 3 is not installed. Attempting to install..."
        if brew install python3; then
            echo "Python 3 installation successful."
            return 0
        else
            echo "Failed to install Python 3."
            return 1
        fi
    fi
}

# Function to check if Python 3 exists, and install if necessary (Debian-based Linux)
check_python_debian() {
    if command -v python3 &>/dev/null; then
        echo "Python 3 is already installed."
        return 0
    else
        echo "Python 3 is not installed. Attempting to install..."
        if sudo apt-get update && sudo apt-get install -y python3; then
            echo "Python 3 installation successful."
            return 0
        else
            echo "Failed to install Python 3."
            return 1
        fi
    fi
}

# Function to check if Python 3 exists, and install if necessary (Red Hat-based Linux)
check_python_redhat() {
    if command -v python3 &>/dev/null; then
        echo "Python 3 is already installed."
        return 0
    else
        echo "Python 3 is not installed. Attempting to install..."
        if sudo yum install -y python3; then
            echo "Python 3 installation successful."
            return 0
        else
            echo "Failed to install Python 3."
            return 1
        fi
    fi
}

# Function to check if pip3 exists, and install if necessary (macOS)
check_pip_macos() {
    if command -v pip3 &>/dev/null; then
        echo "pip3 is already installed."
        return 0
    else
        echo "pip3 is not installed. Attempting to install..."
        if brew install pip3; then
            echo "pip3 installation successful."
            return 0
        else
            echo "Failed to install pip3."
            return 1
        fi
    fi
}

# Function to check if pip3 exists, and install if necessary (Debian-based Linux)
check_pip_debian() {
    if command -v pip3 &>/dev/null; then
        echo "pip3 is already installed."
        return 0
    else
        echo "pip3 is not installed. Attempting to install..."
        if sudo apt-get update && sudo apt-get install -y python3-pip; then
            echo "pip3 installation successful."
            return 0
        else
            echo "Failed to install pip3."
            return 1
        fi
    fi
}

# Function to check if pip3 exists, and install if necessary (Red Hat-based Linux)
check_pip_redhat() {
    if command -v pip3 &>/dev/null; then
        echo "pip3 is already installed."
        return 0
    else
        echo "pip3 is not installed. Attempting to install..."
        if sudo yum install -y python3-pip; then
            echo "pip3 installation successful."
            return 0
        else
            echo "Failed to install pip3."
            return 1
        fi
    fi
}

# Function to check if Python 3's venv module exists, and install if necessary (macOS)
check_venv_macos() {
    if python3 -m venv --help &>/dev/null; then
        echo "Python 3 venv module is already installed."
        return 0
    else
        echo "Python 3 venv module is not installed. Attempting to install..."
        if python3 -m pip install virtualenv; then
            echo "Python 3 venv module installation successful."
            return 0
        else
            echo "Failed to install Python 3 venv module."
            return 1
        fi
    fi
}

# Function to check if Python 3's venv module exists, and install if necessary (Debian-based Linux)
check_venv_debian() {
    if python3 -m venv --help &>/dev/null; then
        echo "Python 3 venv module is already installed."
        return 0
    else
        echo "Python 3 venv module is not installed. Attempting to install..."
        if sudo apt-get update && sudo apt-get install -y python3-venv; then
            echo "Python 3 venv module installation successful."
            return 0
        else
            echo "Failed to install Python 3 venv module."
            return 1
        fi
    fi
}

# Function to check if Python 3's venv module exists, and install if necessary (Red Hat-based Linux)
check_venv_redhat() {
    if python3 -m venv --help &>/dev/null; then
        echo "Python 3 venv module is already installed."
        return 0
    else
        echo "Python 3 venv module is not installed. Attempting to install..."
        if sudo yum install -y python3-venv; then
            echo "Python 3 venv module installation successful."
            return 0
        else
            echo "Failed to install Python 3 venv module."
            return 1
        fi
    fi
}
# Call the appropriate function based on the OS

create_venv() {
    echo "Creating virtual environment 'myvenv' on macOS..."
    if python3 -m venv myvenv; then
        echo "Virtual environment 'myvenv' created."
    else
        echo "This is not macOS. Cannot create virtual environment."
    fi
}

install_requirements() {
    echo "Installing requirements..."
    if ./myvenv/bin/pip install -r requirements.txt; then
        echo "Requirements installed."
    else
        echo "requirements.txt file not found."
    fi
}

# Function to create a one-file executable using PyInstaller
create_executable() {
    if [ -f "app.py" ]; then
        echo "Creating one-file executable using PyInstaller..."
        ./myvenv/bin/pyinstaller --onefile --add-data "resources:resources" --add-data "appresources:appresources" "app.py"
        echo "Executable created."
    else
        echo "app.py file not found."
    fi
}
main() {
    if check_macos; then
        if check_python_macos; then
            if check_pip_macos; then
                if check_venv_macos; then
                    if create_venv; then
                        if install_requirements; then
                            create_executable
                        fi
                    fi
                fi
            fi
        fi
    elif check_debian; then
        if check_python_debian; then
            if check_pip_debian; then
                if check_venv_debian; then
                    if create_venv; then
                        if install_requirements; then
                            create_executable
                        fi
                    fi
                fi
            fi
        fi
    elif check_redhat; then
        if check_python_redhat; then
            if check_pip_redhat; then
                if check_venv_redhat; then
                    if create_venv; then
                        if install_requirements; then
                            create_executable
                        fi
                    fi 
                fi
            fi
        fi
    fi
}

# Call the main function
main

