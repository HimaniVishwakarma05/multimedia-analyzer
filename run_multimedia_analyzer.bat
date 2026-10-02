@echo off
setlocal

set ROOT=%~dp0
set PYTHON=%ROOT%.venv\Scripts\python.exe

if not exist "%PYTHON%" (
    echo Error: .venv was not found at %PYTHON%
    echo Create the virtual environment first:
    echo   python -m venv .venv
    echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    exit /b 1
)

if "%~1"=="" (
    echo Usage:
    echo   run_multimedia_analyzer.bat image  samples\sample.jpg
    echo   run_multimedia_analyzer.bat audio  samples\audio.mp3
    echo   run_multimedia_analyzer.bat video  samples\video.mp4
    echo   run_multimedia_analyzer.bat video  samples\video.mp4 --play
    echo.
    echo You can also pass the full path to any file.
    exit /b 1
)

set TYPE=%~1
shift

if /I "%TYPE%"=="image" (
    if "%~1"=="" (
        echo Error: image analysis requires a file path.
        exit /b 1
    )
    "%PYTHON%" "%ROOT%multimedia_analyzer.py" "%~1"
    exit /b %ERRORLEVEL%
)

if /I "%TYPE%"=="audio" (
    if "%~1"=="" (
        echo Error: audio analysis requires a file path.
        exit /b 1
    )
    "%PYTHON%" "%ROOT%audio_analyzer.py" "%~1"
    exit /b %ERRORLEVEL%
)

if /I "%TYPE%"=="video" (
    if "%~1"=="" (
        echo Error: video analysis requires a file path.
        exit /b 1
    )
    if /I "%~2"=="--play" (
        "%PYTHON%" "%ROOT%video_analyzer.py" "%~1" --play
    ) else (
        "%PYTHON%" "%ROOT%video_analyzer.py" "%~1"
    )
    exit /b %ERRORLEVEL%
)

rem Default behavior: run the unified analyzer on the given file.
"%PYTHON%" "%ROOT%multimedia_analyzer.py" "%~1"
exit /b %ERRORLEVEL%
