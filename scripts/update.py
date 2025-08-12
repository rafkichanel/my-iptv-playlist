name: Update IPTV Playlist

on:
  schedule:
    - cron: '0 3 * * *'  # Jalankan setiap hari jam 03:00 UTC
  workflow_dispatch:      # Bisa dijalankan manual lewat GitHub UI

jobs:
  update-playlist:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repository
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install requests

    - name: Run playlist update script
      run: |
        python update_playlist.py

    - name: Commit and push changes
      run: |
        git config user.name "github-actions[bot]"
        git config user.email "github-actions[bot]@users.noreply.github.com"
        git add Finalplay_updated.m3u
        git commit -m "Update playlist otomatis via GitHub Actions"
        git push
      continue-on-error: true
