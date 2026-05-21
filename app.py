from flask import Flask, request, jsonify, send_from_directory, send_file
from yt_dlp import YoutubeDL
import os

app = Flask(__name__)

# ---------------- WINDOWS DOWNLOADS FOLDER ----------------

DOWNLOAD_FOLDER = os.path.join(
    os.path.expanduser("~"),
    "Downloads"
)

# ---------------- HOME PAGE ----------------

@app.route("/")
def home():

    return send_from_directory(
        ".",
        "index.html"
    )

# ---------------- CSS ----------------

@app.route("/style.css")
def style():

    return send_from_directory(
        ".",
        "style.css"
    )

# ---------------- DOWNLOAD VIDEO ----------------

@app.route("/download", methods=["POST"])
def download():

    try:

        data = request.json

        url = data.get("url")

        quality = data.get("quality")

        if not url:

            return jsonify({

                "status": "error",

                "error": "No URL Provided"
            })

        # ---------------- QUALITY OPTIONS ----------------

        quality_map = {

            "360p":
                "bestvideo*[height<=360]+bestaudio/best[height<=360]",

            "480p":
                "bestvideo*[height<=480]+bestaudio/best[height<=480]",

            "720p":
                "bestvideo*[height<=720]+bestaudio/best[height<=720]",

            "1080p":
                "bestvideo*[height<=1080]+bestaudio/best[height<=1080]",

            "1440p":
                "bestvideo*[height<=1440]+bestaudio/best[height<=1440]",

            "4K":
                "bestvideo*[height<=2160]+bestaudio/best[height<=2160]",
        }

        # ---------------- SELECT FORMAT ----------------

        selected_format = quality_map.get(
            quality,
            "bestvideo+bestaudio/best"
        )

        # ---------------- yt-dlp OPTIONS ----------------

        options = {

            # BEST QUALITY FORMAT
            "format": selected_format,

            # SAFE WINDOWS FILENAMES
            "windowsfilenames": True,

            "restrictfilenames": True,

            # OUTPUT FILE
            "outtmpl": os.path.join(
                DOWNLOAD_FOLDER,
                "%(title)s_%(resolution)s.%(ext)s"
            ),

            # FORCE MP4 OUTPUT
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

            # FASTER DOWNLOADS
            "concurrent_fragment_downloads": 8,

            # ENABLE MORE YOUTUBE FORMATS
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android",
                        "web",
                        "tv"
                    ]
                }
            },

            # ENABLE DASH STREAMS
            "youtube_include_dash_manifest": True,

            # NO PLAYLIST
            "noplaylist": True,

            # FORCE FORMAT SORTING
            "format_sort_force": True,

            # SMART FORMAT SORTING
            "format_sort": [

                # Prefer H264
                "codec:h264",

                # Higher resolution
                "res",

                # Better FPS
                "fps",

                # Better HDR
                "hdr:12",

                # Better audio
                "channels"
            ],

            # PREFER BETTER FORMATS
            "prefer_free_formats": False,

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

            # GET FINAL FILE NAME

            final_filename = ydl.prepare_filename(info)

            # FORCE MP4 FILE

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
        port=port
    )