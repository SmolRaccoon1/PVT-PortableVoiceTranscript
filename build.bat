@echo off
setlocal
cd /d "%~dp0"
py -3.11 -m venv .build
call .build\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
python -c "from huggingface_hub import snapshot_download; snapshot_download('Systran/faster-whisper-small', local_dir='model')"
pyinstaller --noconfirm --clean --onedir --windowed --name VoiceTranscript --collect-all faster_whisper --collect-all av --add-data "model;model" app.py
powershell -NoProfile -Command "Compress-Archive -Path 'dist\VoiceTranscript\*' -DestinationPath 'VoiceTranscript-portable.zip' -Force"
echo.
echo OK: VoiceTranscript-portable.zip
pause
