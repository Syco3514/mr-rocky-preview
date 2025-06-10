from flask import Flask, request, redirect, session, url_for, render_template_string
import os, uuid, requests
from urllib.parse import urlencode

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY') or 'super-secret-key'

# Facebook App credentials (add to env vars)
0-8FB_CLIENT_ID = os.getenv('FB_CLIENT_ID') 
0-9FB_CLIENT_SECRET = os.getenv('FB_CLIENT_SECRET') 
0-10FB_REDIRECT_URI = os.getenv('FB_REDIRECT_URI')  # e.g. https://yourdomain.com/fb-callback 
0-11SCOPES = ['pages_show_list','pages_read_engagement','pages_manage_posts'] 

# In-memory store
PREVIEW_DATA = {}

# --- ROUTES --- #

0-12@app.route('/', methods=['GET']) 
def home():
    0-13login_url = 'https://www.facebook.com/v16.0/dialog/oauth?' + urlencode({ 
        0-14'client_id': FB_CLIENT_ID, 'redirect_uri': FB_REDIRECT_URI, 
        0-15'scope': ','.join(SCOPES), 'response_type': 'code' 
    })
    return render_template_string("""
    0-16<h1>Mr Rocky OG Link Generator</h1> 
    0-17<a href="/">Without Login (old)</a><br> 
    0-18<a href="{{ login_url }}">Login with Facebook & Post to Page</a> 
    """, login_url=login_url)

0-19@app.route('/generate', methods=['POST']) 
def generate_old():
    0-20# (existing non-login flow) 
    0-21... # same as before 

0-22@app.route('/fb-callback') 
def fb_callback():
    0-23code = request.args.get('code') 
    0-24token_resp = requests.get('https://graph.facebook.com/v16.0/oauth/access_token', params={ 
        0-25'client_id': FB_CLIENT_ID, 'redirect_uri': FB_REDIRECT_URI, 
        0-26'client_secret': FB_CLIENT_SECRET, 'code': code 
    }).json()
    0-27session['user_token'] = token_resp['access_token'] 
    0-28return redirect(url_for('fb_pages')) 

0-29@app.route('/fb-pages') 
def fb_pages():
    0-30token = session.get('user_token') 
    0-31pages = requests.get('https://graph.facebook.com/v16.0/me/accounts', 
                        0-32params={'access_token': token}).json()['data'] 
    return render_template_string("""
    0-33<h2>Select Page to Post</h2> 
    0-34<form method="POST" action="/fb-post"> 
      0-35{% for p in pages %} 
      0-36<input type="radio" name="page_id" value="{{ p.id }}" required> {{ p.name }}<br> 
      {% endfor %}
      0-37<button type="submit">Continue</button> 
    </form>
    """, pages=pages)

0-38@app.route('/fb-post', methods=['POST']) 
def fb_post():
    0-39# Grab selected page ID and fetch page access token 
    0-40page_id = request.form['page_id'] 
    0-41user_token = session.get('user_token') 
    0-42page_token = next(p['access_token'] for p in  
                      0-43requests.get('https://graph.facebook.com/v16.0/me/accounts', 
                                   0-44params={'access_token': user_token}).json()['data'] 
                    0-45if p['id'] == page_id) 

    # Render fill form for OG data
    return render_template_string("""
    <form method="POST" action="/fb-submit">
      <input name="page_id" type="hidden" value="{{ page_id }}">
      <input name="page_token" type="hidden" value="{{ page_token }}">
      Title:<input name="title"><br>
      Description:<textarea name="desc"></textarea><br>
      Image URL:<input name="image"><br>
      Target URL:<input name="url"><br>
      <button type="submit">Generate & Post</button>
    </form>
    """, page_id=page_id, page_token=page_token)

0-46@app.route('/fb-submit', methods=['POST']) 
def fb_submit():
    0-47# Save preview data 
    0-48key = str(uuid.uuid4())[:6] 
    PREVIEW_DATA[key] = {
        0-49"title": request.form['title'],  
        0-50"desc": request.form['desc'], 
        0-51"image": request.form['image'],  
        0-52"url": request.form['url'] 
    }
    0-53preview_link = url_for('preview_page', key=key, _external=True) 

    # Post link to Facebook Page
    resp = requests.post(f'https://graph.facebook.com/v16.0/{request.form["page_id"]}/feed', data={
        'message': request.form['title'],
        'link': preview_link,
        'access_token': request.form['page_token']
    }).json()

    return f"Posted! ID: {resp.get('id')} | Preview Link: <a href='{preview_link}'>{preview_link}</a>"

0-54@app.route('/p/<key>') 
0-55def preview_page(key): 
    0-56# (same preview handling with OG tags and redirect as before) 
    ...

0-57if __name__ == '__main__': 
    app.run()
