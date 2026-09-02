import os
import sys
from mutagen import File

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def analyze_audio(audio_path):
    if not os.path.exists(audio_path):
        print(f"Error: File '{audio_path}' not found.")
        return

    file_name = os.path.basename(audio_path)
    file_size = format_size(os.path.getsize(audio_path))
    container = os.path.splitext(file_name)[1].upper().replace('.', '')

    try:
        audio_full = File(audio_path)
        if audio_full is None or not hasattr(audio_full, "info"):
            print("Error: The file is not a supported or valid audio file.")
            return
        
        duration_sec = audio_full.info.length
        minutes = int(duration_sec // 60)
        seconds = int(duration_sec % 60)
        duration = f"{minutes}m {seconds}s ({duration_sec:.2f} seconds)"
        
        sample_rate = f"{audio_full.info.sample_rate} Hz" if hasattr(audio_full.info, 'sample_rate') else "N/A"
        channels = f"{audio_full.info.channels} Channels" if hasattr(audio_full.info, 'channels') else "N/A"
        bitrate = f"{audio_full.info.bitrate // 1000} kbps" if hasattr(audio_full.info, 'bitrate') and audio_full.info.bitrate else "N/A"

        print("================================")
        print("AUDIO METADATA REPORT")
        print("================================")
        print(f"File Name       : {file_name}")
        print(f"File Size       : {file_size}")
        print(f"Container       : {container}")
        print(f"Duration        : {duration}")
        print("\nAUDIO PROPERTIES")
        print("--------------------------------")
        print(f"Sample Rate     : {sample_rate}")
        print(f"Channels        : {channels}")
        print(f"Bit Rate        : {bitrate}")
        
    except Exception as e:
        print(f"Error: Could not read audio metadata. The file may be corrupted or not a valid {container} file.")
        print(f"Details: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python audio_analyzer.py <audio-path>")
        sys.exit(1)

    analyze_audio(sys.argv[1])