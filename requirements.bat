@echo off

REM Check if Python is already installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python...
    REM Download Python installer (change the URL if needed)
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://www.python.org/ftp/python/3.10.2/python-3.10.2-amd64.exe', 'python_installer.exe')"
    
    REM Install Python silently
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
) else (
    echo Python is already installed.
)

REM Check if pip is installed
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing pip...
    REM Download get-pip.py (change the URL if needed)
    powershell -Command "(New-Object Net.WebClient).DownloadFile('https://bootstrap.pypa.io/get-pip.py', 'get-pip.py')"
    
    REM Install pip
    python get-pip.py
    del get-pip.py
) else (
    echo pip is already installed.
)

REM Install required Python libraries using pip
pip install pynput
pip install pywin32

REM Check if the libraries are installed successfully
if errorlevel 1 (
    echo Error: Failed to install required libraries.
) else (
    echo Required libraries installed successfully.
)
