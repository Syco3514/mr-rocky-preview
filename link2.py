from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Mr Rocky Link Generator</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        input, button { padding: 10px; margin: 10px; width: 80%%; max-width: 400px; }
        .container { max-width: 500px; margin: auto; }
        h1 { color: #333; }
        .logo { font-size: 24px; font-weight: bold; color: #007BFF; }
        .link-box { background: #f2f2f2; padding: 10px; word-break: break-all; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🔗 Mr Rocky Link Preview</div>
        <h1>Create a Link with Preview</h1>
        <form action="/generate" method="post" target="_blank">
            <input type="text" name="title" placeholder="Enter Title" required><br>
            <input type="text" name="desc" placeholder="Enter Description" required><br>
            <input type="url" name="img" placeholder="Enter Image URL" required><br>
            <input type="url" name="url" placeholder="Enter Target URL" required><br>
            <button type="submit">Generate Preview Link</button>
        </form>
    </div>
</body>
</html>
"""

HTML_PREVIEW = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta property="og:title" content="{{ title }}">
  <meta property="og:description" content="{{ desc }}">
  <meta property="og:image" content="{{ image }}">
  <meta property="og:type" content="website">
  <meta http-equiv="refresh" content="2;url={{ url }}">
  <title>{{ title }}</title>
  <style>
    body { font-family: sans-serif; text-align: center; padding-top: 50px; }
    img { max-width: 300px; margin-top: 20px; }
    .logo { font-size: 20px; font-weight: bold; color: #007BFF; margin-bottom: 20px; }
  </style>
</head>
<body>
  <div class="logo">Mr Rocky</div>
  <h2>Redirecting to your site...</h2>
  <p>If you are not redirected, <a href="{{ url }}" target="_blank">click here</a>.</p>
  <img src="{{ image }}" alt="Preview Image">
</body>
</html>
"""

@app.route("/")
def form():
    return render_template_string(HTML_FORM)

@app.route("/generate", methods=["POST"])
def generate():
    title = request.form.get("title")
    desc = request.form.get("desc")
    image = request.form.get("img")
    url = request.form.get("url")

    # Create final preview link
    full_url = url_for("preview", title=title, desc=desc, img=image, url=url, _external=True)
    return f"""
    <html>
    <head><title>Generated Link</title></head>
    <body style='text-align:center; padding-top:50px; font-family:sans-serif;'>
      <h2>Your preview link is ready 🎉</h2>
      <div class="link-box" style="padding:10px; background:#f2f2f2; margin:20px auto; width:80%; max-width:600px;">
        <a href="{full_url}" target="_blank">{full_url}</a>
      </div>
      <p>Share this link on social media or click to test it.</p>
    </body>
    </html>
    """

@app.route("/preview")
def preview():
    title = request.args.get("title", "Default Title")
    desc = request.args.get("desc", "Default Description")
    image = request.args.get("img", "https://via.placeholder.com/600x400.png?text=Preview+Image")
    url = request.args.get("url", "https://example.com")
    return render_template_string(HTML_PREVIEW, url=url, title=title, desc=desc, image=image)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)