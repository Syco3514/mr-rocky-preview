from flask import Flask, request, render_template_string, redirect, url_for
import os
import uuid

app = Flask(__name__)

# In-memory store for previews
PREVIEW_DATA = {}

# Template for the OG preview page
OG_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta property="og:title" content="{{ title }}">
  <meta property="og:description" content="{{ desc }}">
  <meta property="og:image" content="{{ image }}">
  <meta property="og:type" content="website">
  <meta http-equiv="refresh" content="3;url={{ url }}">
  <title>{{ title }}</title>
  <style>
    body { font-family: sans-serif; text-align: center; padding-top: 50px; }
    img { max-width: 300px; margin-top: 20px; }
  </style>
</head>
<body>
  <h2>Redirecting to your site...</h2>
  <p>If you are not redirected, <a href="{{ url }}">click here</a>.</p>
  <img src="{{ image }}" alt="Preview Image">
</body>
</html>
"""

# Form page
FORM_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Mr Rocky OG Link Generator</title>
  <style>
    body { font-family: sans-serif; padding: 2rem; text-align: center; }
    input, textarea { width: 300px; padding: 0.5rem; margin: 0.5rem 0; }
    button { padding: 0.7rem 1.5rem; font-weight: bold; }
    .logo { font-size: 2rem; font-weight: bold; margin-bottom: 1rem; color: #333; }
  </style>
</head>
<body>
  <div class="logo">Mr Rocky 🔗</div>
  <form method="POST" action="/generate">
    <input name="title" placeholder="Enter Title" required><br>
    <textarea name="desc" placeholder="Enter Description" required></textarea><br>
    <input name="image" placeholder="Enter Image URL" required><br>
    <input name="url" placeholder="Enter Target URL" required><br>
    <button type="submit">Generate Preview Link</button>
  </form>
</body>
</html>
"""

# Home: form input
@app.route("/", methods=["GET"])
def home():
    return FORM_HTML

# Generate preview and save data
@app.route("/generate", methods=["POST"])
def generate():
    title = request.form["title"]
    desc = request.form["desc"]
    image = request.form["image"]
    url = request.form["url"]

    # Create a unique key
    key = str(uuid.uuid4())[:6]

    # Save data to dictionary
    PREVIEW_DATA[key] = {
        "title": title,
        "desc": desc,
        "image": image,
        "url": url
    }

    # Return full preview link
    full_url = request.url_root + "p/" + key
    return f"""
    <p>✅ Preview link generated:</p>
    <p><a href="{full_url}" target="_blank">{full_url}</a></p>
    <p>Share this link on Facebook, WhatsApp, etc.</p>
    """

# Serve actual OG preview page
@app.route("/p/<key>")
def preview_page(key):
    data = PREVIEW_DATA.get(key)
    if not data:
        return "❌ Preview not found", 404
    return render_template_string(OG_TEMPLATE, **data)

# Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
