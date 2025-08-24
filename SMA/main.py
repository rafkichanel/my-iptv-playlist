import requests
from pathlib import Path
from datetime import datetime

# Path file URL playlist (di root repo)
URL_FILE = Path(__file__).parent.parent / "playlist_url.txt"

# File playlist output
OUTPUT_FILE = Path(__file__).parent.parent / "playlist.m3u"

def read_url(file_path: Path) -> str:
    if not file_path.exists():
        print(f"File {file_path} tidak ditemukan. Silakan buat dan masukkan URL playlist.")
        return ""
    return file_path.read_text().strip()

def download_playlist(url: str, save_path: Path):
    if not url:
        print("URL kosong. Tidak ada playlist yang di-download.")
        return
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        save_path.write_text(response.text, encoding="utf-8")
        print(f"[{datetime.now()}] Playlist berhasil diperbarui: {save_path}")
    except requests.RequestException as e:
        print(f"[{datetime.now()}] Gagal download playlist: {e}")

if __name__ == "__main__":
    playlist_url = read_url(URL_FILE)
    download_playlist(playlist_url, OUTPUT_FILE)
