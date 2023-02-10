@echo off
cd simulator
call activate simulator
set /p "name=Enter config file name: "
python simulate.py %name%
pause