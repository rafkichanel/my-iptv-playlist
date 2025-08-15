name: Update M3U Playlist

on:
  push:
    branches:
      - main
  schedule:
    - cron: '0 */6 * * *' # Run every 6 hours
  workflow_dispatch: # Allows manual trigger

jobs:
  update-playlist:
    runs-on: ubuntu-latest
    permissions:
      contents: write # This is crucial for the script to be able to push changes

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10' # Use a recent stable Python version

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install aiohttp

      - name: Run Python script
        run: python main.py

