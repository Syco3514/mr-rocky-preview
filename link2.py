from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

PREVIEW_DATA = {}

# Home Page (Form UI)
@app.route("/", methods=["GET"])
def home():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>Mr Rocky OG Link Generator</title>
      <style>
        body {
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          background: linear-gradient(to right, #667eea, #764ba2);
          color: #fff;
          display: flex;
          justify-content: center;
          align-items: center;
          height: 100vh;
          margin: 0;
        }
        .container {
          background: rgba(0, 0, 0, 0.4);
          padding: 2rem 3rem;
          border-radius: 1rem;
          box-shadow: 0 4px 30px rgba(0,0,0,0.1);
          width: 90%;
          max-width: 500px;
        }
        h1 {
          text-align: center;
          margin-bottom: 1rem;
        }
        input, textarea {
          width: 100%;
          padding: 0.8rem;
          margin: 0.5rem 0;
          border: none;
          border-radius: 8px;
        }
        input[type="file"] {
          background-color: #fff;
          color: #000;
        }
        button {
          width: 100%;
          padding: 0.8rem;
          margin-top: 1rem;
          background-color: #48bb78;
          border: none;
          border-radius: 8px;
          font-size: 1rem;
          font-weight: bold;
          cursor: pointer;
        }
        button:hover {
          background-color: #38a169;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <h1>🔗 Mr Rocky Link Generator</h1>
        <form method="POST" action="/generate" enctype="multipart/form-data">
          <input type="text" name="title" placeholder="Enter Title" required>
          <textarea name="desc" placeholder="Enter Description" rows="3" required></textarea>
          <input type="file" name="image_file" accept="image/*">
          <input type="text" name="image_url" placeholder="Or enter Image URL">
          <input type="text" name="url" placeholder="Enter Target URL" required>
          <button type="submit">Generate Preview Link</button>
        </form>
      </div>
    </body>
    </html>
    """

# Generate preview
@app.route("/generate", methods=["POST"])
def generate():
    title = request.form["title"]
    desc = request.form["desc"]
    target_url = request.form["url"]

    image_url = request.form.get("image_url")
    image_file = request.files.get("image_file")

    if image_file and image_file.filename != "":
        ext = os.path.splitext(image_file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        image = url_for('uploaded_file', filename=filename, _external=True)
    elif image_url:
        image = image_url
    else:
        return "❌ Image required (upload or URL)", 400

    key = str(uuid.uuid4())[:6]
    PREVIEW_DATA[key] = {
        "title": title,
        "desc": desc,
        "image": image,
        "url": target_url
    }

    full_url = request.url_root + "p/" + key
    return f"""
    <html>
    <head>
    <style>
      body {{ font-family: sans-serif; text-align: center; padding-top: 100px; }}
      a {{ font-size: 1.2rem; color: #2b6cb0; }}
    </style>
    </head>
    <body>
      <h2>✅ Preview Link Generated!</h2>
      <p><a href="{full_url}" target="_blank">{full_url}</a></p>
      <p>Share it on Facebook, WhatsApp, etc.</p>
    </body>
    </html>
    """

# Serve uploaded files
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Preview route
@app.route("/p/<key>")
def preview_page(key):
    data = PREVIEW_DATA.get(key)
    if not data:
        return "❌ Preview not found", 404

    user_agent = request.headers.get('User-Agent', '').lower()
    is_facebook = 'facebookexternalhit' in user_agent or 'facebot' in user_agent

    if is_facebook:
        return render_template_string("""
        <html prefix="og: http://ogp.me/ns#">
        <head>
          <meta charset="utf-8">
          <meta property="og:title" content="{{ title }}">
          <meta property="og:description" content="{{ desc }}">
          <meta property="og:image" content="{{ image }}">
          <meta property="og:type" content="website">
          <meta property="og:url" content="{{ url }}">
          <title>{{ title }}</title>
        </head>
        <body>
          Facebook crawler detected.
        </body>
        </html>
        """, **data)

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta property="og:title" content="{{ title }}">
      <meta property="og:description" content="{{ desc }}">
      <meta property="og:image" content="{{ image }}">
      <meta property="og:type" content="website">
      <meta property="og:url" content="{{ url }}">
      <title>{{ title }}</title>
      <style>
        body {
          margin: 0;
          padding: 0;
          font-family: sans-serif;
          background-image: url('{{ image }}');
          background-repeat: repeat-y;
          background-size: contain;
          background-position: center top;
          height: 100vh;
          color: white;
          text-shadow: 1px 1px 3px black;
          display: flex;
          flex-direction: column;
          justify-content: center;
          align-items: center;
          backdrop-filter: blur(1px);
        }
        .overlay {
          background-color: rgba(0, 0, 0, 0.5);
          padding: 2rem;
          border-radius: 1rem;
        }
        a {
          color: yellow;
        }
      </style>
      <script>
        setTimeout(function() {
          window.location.href = "{{ url }}";
        }, 3000);
      </script>
    </head>
    <body>
      <div class="overlay">
        <h2>Redirecting to your site...</h2>
        <p>If not redirected, <a href="{{ url }}">click here</a>.</p>
      </div>
    </body>
    </html>
    """, **data)

# Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
