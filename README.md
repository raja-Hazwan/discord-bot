# 🎵 Discord Music Bot

A powerful and stylish Discord music bot built with Python, `discord.py`, and `yt-dlp`. It supports YouTube playback, a music queue, looping, and interactive **button-based controls** — all displayed in a sleek **embed UI** with track thumbnails and duration.

---

## 🚀 Features

- ✅ `!play [song or link]` — Plays or queues a YouTube track
- 🎛️ Interactive buttons (Pause, Resume, Skip, Loop)
- 📜 `!queue` — Shows the current song queue
- 🔁 `!loop` — Toggles looping for the current track
- ⏸️ `!pause`, ▶️ `!resume`, ⏭ `!skip`, 👋 `!leave`
- 🖼️ Embed UI with:
  - Track title
  - Duration (formatted)
  - Large video thumbnail

---

## 📸 Sample UI

<img src="https://user-images.githubusercontent.com/your-screenshot.png" width="600">

---

## 📦 Requirements

- Python 3.8 or higher
- FFmpeg installed and accessible via system PATH
- Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)

---

## 🧠 Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/your-username/discord-music-bot.git
cd discord-music-bot
```
### 2.Install dependencies
```bash
pip install -r requirements.txt
```
Make sure ffmpeg is installed.

    Windows: Download FFmpeg → Add ffmpeg/bin to PATH

    macOS: brew install ffmpeg

    Linux: sudo apt install ffmpeg

### 3. Set up environment variables

Create a .env file in the project root:

DISCORD_TOKEN=your_discord_bot_token_here

    Never share your token. Keep .env in .gitignore (already configured).
