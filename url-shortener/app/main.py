# app/main.py

from flask import Flask, request, jsonify, redirect
from app.models import store_url, get_url_data, increment_click
from app.utils import validate_url

app = Flask(__name__)
@app.route('/')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "URL Shortener API"
    })

@app.route('/api/health')
def api_health():
    return jsonify({
        "status": "ok",
        "message": "URL Shortener API is running"
    })

@app.route("/api/shorten", methods=["POST"])
def shorten():
    data = request.get_json()
    original_url = data.get("url")

    if not original_url or not validate_url(original_url):
        return jsonify({"error": "Invalid URL"}), 400

    short_code = store_url(original_url)
    short_url = f"http://localhost:5000/{short_code}"
    return jsonify({"short_code": short_code, "short_url": short_url})

@app.route("/<short_code>")
def redirect_short_url(short_code):
    url_data = get_url_data(short_code)
    if not url_data:
        return jsonify({"error": "Short code not found"}), 404

    increment_click(short_code)
    return redirect(url_data["url"], code=302)

@app.route("/api/stats/<short_code>")
def stats(short_code):
    url_data = get_url_data(short_code)
    if not url_data:
        return jsonify({"error": "Short code not found"}), 404

    return jsonify({
        "url": url_data["url"],
        "clicks": url_data["clicks"],
        "created_at": url_data["created_at"]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)