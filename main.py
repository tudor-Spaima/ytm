import os
import threading
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Static, DataTable
from ytmusicapi import YTMusic
import tools  # Import the tools module for downloading


class YouTubeMusicPlaylistApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ytmusic = YTMusic()
        self.playlist_data = None
        self.playlist_url = None  # To store the playlist URL for downloading
        self.download_folder = os.path.expanduser("~/Downloads")  # Default download folder

    def compose(self) -> ComposeResult:
        # Define the UI structure
        yield Header()
        yield Static("Enter YouTube Music Playlist URL below:", id="instruction")
        yield Input(placeholder="Enter YouTube Music Playlist Link", id="playlist_link")
        yield Button("Load Playlist", id="load_button")
        yield DataTable(id="playlist_table", show_header=True)
        yield Button("Download Playlist", id="download_button")  # Button to trigger download
        yield Static(id="status")
        yield Footer()

    def on_mount(self) -> None:
        # Called after the application is mounted
        self.query_one("#playlist_table", DataTable).add_columns("No.", "Song", "Artist", "Duration")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "load_button":
            playlist_link = self.query_one("#playlist_link", Input).value
            self.playlist_url = playlist_link  # Save the playlist URL for download
            playlist_id = self.extract_playlist_id(playlist_link)

            if playlist_id:
                self.load_playlist(playlist_id)
            else:
                self.update_status("Invalid YouTube Music Playlist URL.")

        elif event.button.id == "download_button":
            if self.playlist_url and self.download_folder:
                # Start the download process in a new thread
                threading.Thread(target=self.download_playlist, args=(self.playlist_url, self.download_folder)).start()
            else:
                self.update_status("Playlist URL or download folder not selected.")

    def extract_playlist_id(self, url: str) -> str:
        import re
        # Extract playlist ID from YouTube Music URL
        match = re.search(r"list=([a-zA-Z0-9_-]+)", url)
        return match.group(1) if match else None

    def load_playlist(self, playlist_id: str) -> None:
        try:
            # Fetch playlist information using YTMusicAPI
            playlist_info = self.ytmusic.get_playlist(playlist_id)
            playlist_title = playlist_info['title']
            tracks = playlist_info['tracks']

            # Update playlist info
            table = self.query_one("#playlist_table", DataTable)
            table.clear()

            for idx, track in enumerate(tracks, start=1):
                song_title = track['title']
                artist_name = ", ".join(artist['name'] for artist in track['artists'])
                duration = track['duration']  # Duration of the song
                table.add_row(str(idx), song_title, artist_name, duration)

            self.update_status(f"Loaded playlist: {playlist_title}")

        except Exception as e:
            self.update_status(f"Error loading playlist: {e}")

    def download_playlist(self, playlist_url: str, download_folder: str) -> None:
        try:
            self.update_status(f"Starting download from {playlist_url} to {download_folder}...")

            # Call the download process from the tools module
            tools.download_proceess(playlist_url)

            self.update_status(f"Download completed for playlist from {playlist_url}")
        except Exception as e:
            self.update_status(f"Error during download: {e}")

    def update_status(self, message: str) -> None:
        # Update the status bar with messages
        status = self.query_one("#status", Static)
        status.update(message)


if __name__ == "__main__":
    app = YouTubeMusicPlaylistApp()
    app.run()
