
# Check if git is available
if (-not (Test-Path -Path "C:\Program Files\Git\cmd\git.exe")) {
    Write-Host "GIT not available, Installing now..."
    # Install git
    Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.33.1.windows.1/Git-2.33.1-64-bit.exe" -OutFile "$env:TEMP\Git-2.33.1-64-bit.exe"
    Start-Process -FilePath "$env:TEMP\Git-2.33.1-64-bit.exe" -ArgumentList "/VERYSILENT" -Wait
    if (-not (Test-Path -Path "C:\Program Files\Git\cmd\git.exe")) {
        Write-Host "GIT installation Failed"
    } else {
        Write-Host "GIT Installation Successful"
    }
} else {
    Write-Host "GIT available"
}


Write-Host "Installing Python3.11.9"
Invoke-WebRequest -UseBasicParsing -Uri 'https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe' -OutFile 'c:/python-3.11.9-amd64.exe'

# Install Python via command prompt
Start-Process -FilePath 'c:/python-3.11.9-amd64.exe' -ArgumentList '/quiet', 'InstallAllUsers=1', 'PrependPath=1', 'Include_test=0' -Wait

# Set Python location
setx /M path "$env:path;C:\Program Files\Python311"

$env:PATH = $env:PATH + ";C:\Program Files\Python311"
Write-Host "Python installation completed"

Start-Process -FilePath "C:\Program Files\Python311\Scripts\pip3.exe" -ArgumentList 'install', 'virtualenv' -Wait
Write-Host "virtualenv installed successfully."


rite-Output "Cloning repository..."
Start-Process -FilePath "C:\Program Files\Git\cmd\git.exe" -ArgumentList "clone", "https://github.com/neuroneural/immunetworksapp.git" -NoNewWindow -Wait

# Change directory to immunetworksapp
cd immunetworksapp

# Create new virtual environment
Write-Output "Creating virtual environment (myvnv)..."
Start-Process -FilePath "C:\Program Files\Python311\Scripts\virtualenv.exe" -ArgumentList "myvnv"

& .\myvnv\Scripts\Activate.ps1
# Install requirements in the virtual environment
Write-Output "Installing requirements in the virtual environment..."
& pip install -r requirements.txt

# Run pyinstaller within the virtual environment
Write-Output "Running pyinstaller within the virtual environment..."
& "pyinstaller" --onefile --add-data "resources:resources" --add-data "appresources:appresources" "app.py"

& deactivate