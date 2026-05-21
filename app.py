from flask import Flask, request, jsonify, send_from_directory, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

# ---------------- BASE DIRECTORY ----------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ---------------- DOWNLOAD FOLDER ----------------

DOWNLOAD_FOLDER = "/tmp/downloads"

# CREATE DOWNLOAD FOLDER

os.makedirs(
    DOWNLOAD_FOLDER,
    exist_ok=True
)

# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    return send_from_directory(
        BASE_DIR,
        "index.html"
    )

# ---------------- CSS ----------------

@app.route("/style.css")
def style():

    return send_from_directory(
        BASE_DIR,
        "style.css"
    )

# ---------------- DOWNLOAD VIDEO ----------------

@app.route("/download", methods=["POST"])
def download():

    try:

        data = request.json

        url = data.get("url")

        quality = data.get("quality")

        # ---------------- VALIDATION ----------------

        if not url:

            return jsonify({

                "status": "error",

                "error": "No URL Provided"
            })

        # ---------------- QUALITY OPTIONS ----------------

        quality_map = {

            "360p":
                "bestvideo*[height<=360]+bestaudio/best[height<=360]/best",

            "480p":
                "bestvideo*[height<=480]+bestaudio/best[height<=480]/best",

            "720p":
                "bestvideo*[height<=720]+bestaudio/best[height<=720]/best",

            "1080p":
                "bestvideo*[height<=1080]+bestaudio/best[height<=1080]/best",

            "1440p":
                "bestvideo*[height<=1440]+bestaudio/best[height<=1440]/best",

            "4K":
                "bestvideo*[height<=2160]+bestaudio/best[height<=2160]/best",
        }

        # ---------------- SELECT FORMAT ----------------

        selected_format = quality_map.get(
            quality,
            "bestvideo+bestaudio/best"
        )

        # ---------------- yt-dlp OPTIONS ----------------

        options = {

            # VIDEO QUALITY
            "format": selected_format,

            # YOUTUBE COOKIES
            "cookiefile": "cookies.txt",

            # BETTER RENDER COMPATIBILITY
            "http_headers": {
                "User-Agent": "Mozilla/5.0"
            },

            # BETTER YOUTUBE EXTRACTION
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "web"
                    ]
                }
            },

            # SAFE WINDOWS FILENAMES
            "windowsfilenames": True,

            "restrictfilenames": True,

            # OUTPUT FILE
            "outtmpl": os.path.join(
                DOWNLOAD_FOLDER,
                "%(title)s_%(resolution)s.%(ext)s"
            ),

            # FORCE MP4
            "merge_output_format": "mp4",

            # AUTO CONVERT TO MP4
            "postprocessors": [{

                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp4"
            }],

            # BETTER STABILITY
            "retries": 30,

            "fragment_retries": 30,

            "extractor_retries": 10,

            "socket_timeout": 120,

            # REDUCE BOT DETECTION
            "concurrent_fragment_downloads": 1,

            "sleep_interval": 2,

            "max_sleep_interval": 5,

            "source_address": "0.0.0.0",

            # ENABLE DASH
            "youtube_include_dash_manifest": True,

            # NO PLAYLIST
            "noplaylist": True,

            # KEEP TEMP FILES
            "nopart": False,

            # SHOW TERMINAL LOGS
            "quiet": False,
        }

        # ---------------- DOWNLOAD VIDEO ----------------

        with YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

            # FINAL FILE NAME

            final_filename = ydl.prepare_filename(info)

            final_filename = os.path.splitext(
                final_filename
            )[0] + ".mp4"

        return jsonify({

            "status": "success",

            "message": "Download Complete ✅",

            "file": os.path.basename(final_filename)
        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "error": str(e)
        })

# ---------------- SEND FILE TO BROWSER ----------------

@app.route("/file/<filename>")
def get_file(filename):

    path = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    if not os.path.exists(path):

        return jsonify({

            "status": "error",

            "error": "File not found"
        })

    return send_file(
        path,
        as_attachment=True
    )

# ---------------- START SERVER ----------------

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )