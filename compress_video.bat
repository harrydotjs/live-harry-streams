@echo off
cd /d "%~dp0"
title 1-Click Video Compressor (High-Efficiency 1080p H.264)
echo =================================================================
echo   VIDEO COMPRESSOR FOR GITHUB LIVE STREAMING
echo =================================================================
echo.
echo This tool compresses large video files (e.g. 2.5 GB) into a lightweight,
echo high-definition 1080p file (video.mp4) that uploads and streams smoothly.
echo.

set INPUT_FILE=
if exist "input.mp4" set INPUT_FILE=input.mp4
if exist "raw.mp4" set INPUT_FILE=raw.mp4
if exist "large.mp4" set INPUT_FILE=large.mp4
if exist "video_raw.mp4" set INPUT_FILE=video_raw.mp4

if "%INPUT_FILE%"=="" (
    echo Please drag and drop your 2.5 GB video file onto this window and press ENTER:
    set /p INPUT_FILE=Video path: 
)

if "%INPUT_FILE%"=="" (
    echo No video file provided. Exiting.
    pause
    exit /b
)

echo.
echo Starting compression on: %INPUT_FILE%
echo Output target: video.mp4 (High-Quality 1080p H.264)
echo.

ffmpeg -i %INPUT_FILE% -c:v libx264 -crf 23 -preset fast -pix_fmt yuv420p -c:a aac -b:a 192k -ar 44100 -movflags +faststart -y "video.mp4"

if %errorlevel% equ 0 (
    echo.
    echo =================================================================
    echo   SUCCESS! Compressed video created: video.mp4
    echo =================================================================
    echo You can now use video.mp4 with your stream!
) else (
    echo.
    echo [ERROR] FFmpeg compression failed. Check the error above.
)

echo.
pause
