import aiohttp
import asyncio
import base64
import os
import re
from dotenv import load_dotenv
import requests

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "rafkichanel"
REPO_NAME = "my-iptv-playlist"
BRANCH = "master"
FILE_PATH = "Finalplay.m3u"

TIMEOUT = 5
CONCURRENCY = 50

def get_file_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}?ref={BRANCH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(url, headers=headers)
    return r.json().get("sha") if r.status_code == 200 else None

def update_github_file(content, active_count, total_count):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    sha = get_file_sha()
    data = {
        "message": f"Update playlist Finalplay.m3u otomatis (aktif: {active_count}/{total_count})",
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
        "branch": BRANCH,
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, json=data, headers=headers)
    print("Berhasil update di GitHub" if r.status_code in [200, 201] else f"Gagal update: {r.status_code}")

async def fetch_playlist(session, url):
    try:
        async with session.get(url, timeout=TIMEOUT) as resp:
            if resp.status == 200:
                print(f"✅ Download sukses dari {url}")
                return await resp.text()
    except:
        print(f"❌ Gagal download dari {url}")
    return None

async def check_channel(session, line):
    try:
        async with session.get(line.strip(), timeout=TIMEOUT) as resp:
            return resp.status == 200
    except:
        return False

async def main():
    async with aiohttp.ClientSession() as session:
        with open("sources.txt") as f:
            sources = [line.strip() for line in f if line.strip()]

        playlists = await asyncio.gather(*[fetch_playlist(session, url) for url in sources])
        combined = "\n".join(p for p in playlists if p)

        filtered_lines = []
        entries = combined.split("#EXTINF")
        for entry in entries:
            if not entry.strip():
                continue
            if re.search(r"WHATSAPP", entry, re.IGNORECASE):
                continue
            filtered_lines.append("#EXTINF" + entry.strip())

        print(f"Total channel setelah filter: {len(filtered_lines)}")

        active_playlist = []
        total_count = 0
        active_count = 0

        sem = asyncio.Semaphore(CONCURRENCY)
        async def check_and_add(entry):
            nonlocal active_count, total_count
            lines = entry.splitlines()
            if len(lines) < 2:
                return
            url = lines[-1].strip()
            total_count += 1
            async with sem:
                if await check_channel(session, url):
                    active_count += 1
                    active_playlist.append("\n".join(lines))

        await asyncio.gather(*[check_and_add(entry) for entry in filtered_lines])

        final_content = "#EXTM3U\n" + "\n".join(active_playlist)
        update_github_file(final_content, active_count, total_count)

if __name__ == "__main__":
    asyncio.run(main())
