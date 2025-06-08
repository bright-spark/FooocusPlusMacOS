@echo off

set "requirements_txt=%~dp0\requirements.txt"
set "requirements_repair_txt=%~dp0\repair_dependency_list.txt"
set "python_exec=..\..\..\python_embedded\python.exe"
set "aki_python_exec=..\..\python\python.exe"

echo Installing EasyUse Requirements...

if exist "%python_exec%" (
    echo Installing with ComfyUI Portable
    "%python_exec%" -s -m pip install -r "%requirements_txt%"
)^
else (
    echo Installing with Python
    pip install -r "%requirements_txt%"
)
pause
