@echo off
title DraconicWoW Diagnostic Auto-Fixer
color 0B

echo ========================================================
echo DraconicWoW Server Diagnostic Tool
echo ========================================================
echo This script checks your PC for common setup mistakes.
echo Please run this file FROM INSIDE your repack folder!
echo (The folder containing worldserver.exe)
echo ========================================================
echo.

set ERRORS=0

echo Checking MySQL Database Port (3306)...
netstat -ano | findstr :3306 >nul
if %errorlevel% equ 0 (
    echo [OK] Port 3306 is in use (MySQL is likely running).
) else (
    echo [ERROR] Port 3306 is NOT in use. Make sure you started MySQL in UniController!
    set /A ERRORS+=1
)

echo.
echo Checking for Server Executables...
if exist "worldserver.exe" (
    echo [OK] worldserver.exe found.
) else (
    echo [ERROR] worldserver.exe NOT found. Are you running this script in the RelWithDebInfo folder?
    set /A ERRORS+=1
)

if exist "bnetserver.exe" (
    echo [OK] bnetserver.exe found.
) else (
    echo [ERROR] bnetserver.exe NOT found.
    set /A ERRORS+=1
)

echo.
echo Checking Map Data Extraction...
if exist "dbc" (echo [OK] dbc data found.) else (echo [ERROR] No dbc folder found! You must extract maps! & set /A ERRORS+=1)
if exist "maps" (echo [OK] maps data found.) else (echo [ERROR] No maps folder found! You must extract maps! & set /A ERRORS+=1)
if exist "vmaps" (echo [OK] vmaps data found.) else (echo [ERROR] No vmaps folder found! You must extract maps! & set /A ERRORS+=1)
if exist "mmaps" (echo [OK] mmaps data found.) else (echo [WARNING] No mmaps folder found! Npcs might fall through the floor.)

echo.
echo ========================================================
if %ERRORS% equ 0 (
    color 0A
    echo ALL CHECKS PASSED! Your server folder looks correct.
    echo If you still can't connect, make sure your WoW client's
    echo Config.wtf file is set to: SET portal "127.0.0.1"
) else (
    color 0C
    echo FOUND %ERRORS% ERRORS.
    echo Please fix the [ERROR] lines above, or take a screenshot
    echo of this window and post it in the #troubleshooting channel!
)
echo ========================================================
pause
