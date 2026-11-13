
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return "Josua Lossless Add-on is running!"

@app.route("/manifest.json")
def manifest():
    return jsonify({
        "id": "josua.lossless",
        "name": "Josua Lossless",
        "description": "Free legal FLAC music search",
        "version": "1.0.0",
        "types": ["track"],
        "catalogs": [{
            "type": "track",
            "id": "josua-search",
            "name": "Josua Lossless"
        }],
        "resources": ["catalog", "meta", "stream"]
    })

@app.route("/catalog/track/josua-search.json")
def search():
    query = request.args.get("search", "")
    if not query:
        return jsonify({"metas": []})

    url = "https://archive.org/advancedsearch.php"
    params = {
        "q": f'title:({query}) AND mediatype:audio',
        "fl[]": ["identifier", "title"],
        "rows": 20,
        "output": "json"
    }

    data = requests.get(url, params=params, timeout=20).json()
    metas = []

    for item in data["response"]["docs"]:
        metas.append({
            "id": item["identifier"],
            "type": "track",
            "name": item.get("title", "Unknown"),
            "poster": ""
        })

    return jsonify({"metas": metas})

@app.route("/meta/track/<item_id>.json")
def meta(item_id):
    return jsonify({
        "meta": {
            "id": item_id,
            "type": "track",
            "name": item_id
        }
    })

@app.route("/stream/track/<item_id>.json")
def stream(item_id):
    files_url = f"https://archive.org/metadata/{item_id}"
    data = requests.get(files_url, timeout=20).json()

    streams = []
    for f in data.get("files", []):
        name = f.get("name", "")
        if name.lower().endswith(".flac"):
            streams.append({
                "url": f"https://archive.org/download/{item_id}/{name}",
                "title": "FLAC",
                "container": "flac"
            })

    return jsonify({"streams": streams})
  
