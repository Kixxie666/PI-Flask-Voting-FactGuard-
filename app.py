from flask import Flask, render_template, request, redirect, flash
import requests

app = Flask(__name__)
app.secret_key = 'your-secret-key'

AZURE_API_POSTS = 'https://c2025401-eccjh2fxfjbch6hg.uksouth-01.azurewebsites.net/api/community-posts/'
AZURE_API_VOTE_BASE = 'https://c2025401-eccjh2fxfjbch6hg.uksouth-01.azurewebsites.net/vote'

def get_post_id_by_url(target_url):
    try:
        response = requests.get(AZURE_API_POSTS, timeout=5)
        posts = response.json()
        for post in posts:
            if post['url'] == target_url:
                return post['id']
    except Exception:
        return None
    return None

@app.route('/')
def home():
    try:
        response = requests.get(AZURE_API_POSTS, timeout=5)
        urls = response.json()
    except Exception:
        flash('Unable to load community links. Try again later.', 'danger')
        urls = []
    return render_template('index.html', urls=urls)

@app.route('/vote', methods=['POST'])
def vote():
    url_value = request.form.get('url')
    vote_type = request.form.get('vote_type', '').strip().lower()

    if not url_value or vote_type not in ['fake', 'legit']:
        flash('Invalid or missing voting data.', 'danger')
        return redirect('/')

    post_id = get_post_id_by_url(url_value)
    if not post_id:
        flash('Could not match URL to a valid post.', 'danger')
        return redirect('/')

    vote_url = f"{AZURE_API_VOTE_BASE}/{post_id}/"
    payload = {'vote_type': vote_type}

    print("SENDING PAYLOAD TO DJANGO:", payload)

    try:
        response = requests.post(vote_url, json=payload, timeout=5)
        print("Status:", response.status_code)
        print("Response:", response.text)

        if response.status_code == 200:
            flash('Your vote was counted. Thanks!', 'success')
        elif response.status_code == 404:
            flash('That link could not be found in the system.', 'warning')
        else:
            try:
                error_message = response.json().get("message", "Unknown error")
            except Exception:
                error_message = "Server error"
            flash(f'Vote failed: {error_message}', 'danger')
    except Exception as e:
        print("EXCEPTION:", str(e))
        flash('Failed to contact the voting server.', 'danger')

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
