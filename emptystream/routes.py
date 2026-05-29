from flask import Flask, render_template

from .youtube import youtube_bp

app = Flask(__name__)
app.register_blueprint(youtube_bp)


@app.route("/")
def index():
    return render_template("index.html")
