from server import app
from flask import render_template, request
import yt_dlp


@app.route("/")
def form():
    return render_template("downloader.html")


@app.route("/data/", methods=["POST", "GET"])
def data():
    if request.method == "POST":
        form_data = request.form
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ],
            "paths": {"home": "downloads"},
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([form_data["url"]])
        return render_template("data.html", form_data=form_data)
