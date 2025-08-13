import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

# Load daftar sumber dari sources.txt
with open("sources.txt", "r", encoding="utf-8") as f:
    backup_playlist_urls = [line.strip() for line in f if line.strip()]

output_file = "Finalplay.m3u"

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise Exception("Environment variable GITHUB_TOKEN tidak ditemukan!")

REPO_OWNER = "rafkichanel"
REPO_NAME = "my-iptv-playlist"
BRANCH = "master"
FILE_PATH = "Finalplay.m3u"

def download_playlist(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        print(f"Download sukses dari {url}")
        return r.text
    except Exception as e:
        print(f"Gagal download dari {url}: {e}")
        return None

def get_file_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json()["sha"]
    return None

def update_github_file(content):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    sha = get_file_sha()
    data = {
        "message": "Update playlist Finalplay.m3u otomatis",
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": BRANCH,
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, json=data, headers=headers)
    if r.status_code in [200, 201]:
        print("Berhasil update file di GitHub!")
    else:
        print(f"Gagal update file di GitHub: {r.status_code} - {r.text}")

def main():
    playlists = []
    for url in backup_playlist_urls:
        content = download_playlist(url)
        if content:
            # Skip kategori WHATSAPP
            filtered = "\n".join(
                line for line in content.splitlines()
                if "WHATSAPP" not in line.upper()
            )
            playlists.append(filtered)

    if playlists:
        combined = "\n".join(playlists)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(combined)
        print(f"Playlist berhasil disimpan ke {output_file}")
        update_github_file(combined)
    else:
        print("Tidak ada playlist berhasil didownload.")

if __name__ == "__main__":
    main()
