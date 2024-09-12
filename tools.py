import os
import yt_dlp
import json
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1
from tkinter import Tk
from tkinter.filedialog import askdirectory

FOLDER = None  # Global variable for the folder

def download_playlist(playlist_url, download_folder):
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{download_folder}/%(title)s.%(ext)s',  
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'noplaylist': False,
        'writesubtitles': False,
        'writethumbnail': False,
        'writeinfojson': True,  
    }

    # Download the entire playlist from the given URL
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_url])

    # Rename and set MP3 metadata
    rename_and_tag_mp3_files(download_folder)
    # Clean up additional files
    clean_up_files(download_folder)

# Function to rename downloaded files based on the metadata from yt-dlp
def rename_and_tag_mp3_files(download_folder):
    for filename in os.listdir(download_folder):
        if filename.endswith('.mp3'):
            # Get corresponding .info.json file for the metadata
            info_json = filename.replace('.mp3', '.info.json')
            json_path = os.path.join(download_folder, info_json)
            
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)

                try:
                    # Attempt to extract artist name from metadata
                    artist_name = (
                        metadata.get('artist') or  # First try 'artist'
                        metadata.get('uploader') or  # Fallback to 'uploader'
                        metadata.get('channel') or  # Fallback to 'channel'
                        'Unknown Artist'  # Default if not found
                    )

                    # Extract song title, if available, or fallback to 'Unknown Title'
                    song_name = metadata.get('track') or metadata.get('title') or 'Unknown Title'

                    new_filename = f"{song_name} - {artist_name}.mp3"
                    old_file = os.path.join(download_folder, filename)
                    new_file = os.path.join(download_folder, new_filename)

                    os.rename(old_file, new_file)

                    # Add ID3 tags (MP3 metadata)
                    audio = MP3(new_file, ID3=ID3)
                    audio.tags.add(TIT2(encoding=3, text=song_name))  # Set song title tag
                    audio.tags.add(TPE1(encoding=3, text=artist_name))  # Set artist tag
                    audio.save()

                    print(f"Renamed and tagged: {new_filename}")

                except Exception as e:
                    print(f"Error processing metadata for {filename}: {e}")

# Function to clean up unnecessary files like .info.json and .webm
def clean_up_files(download_folder):
    for filename in os.listdir(download_folder):
        if filename.endswith('.info.json') or filename.endswith('.webm'):
            file_path = os.path.join(download_folder, filename)
            try:
                os.remove(file_path)
                print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error deleting {filename}: {e}")


def file_dialog():
    global FOLDER  # Use the global variable
    root = Tk()
    root.withdraw()
    download_folder = askdirectory(title="Select Download Folder")
    FOLDER = download_folder

    if not os.path.exists(download_folder):
        os.makedirs(download_folder)  
    
    print(f"Selected download folder: {download_folder}")

    return download_folder

def download_proceess(playlist_url):
    LOCAL_FOLDER = os.path.dirname(os.path.abspath(__file__))
    FOLDER = os.path.join(LOCAL_FOLDER, 'downloads')

    if os.path.exists(FOLDER):
        import shutil
        shutil.rmtree(FOLDER)
        print(f"Folder '{FOLDER}' and its contents have been deleted.")

    # Now create the folder again
    os.makedirs(FOLDER)
    print(f"Folder '{FOLDER}' has been created.")

    download_playlist(playlist_url, FOLDER)
