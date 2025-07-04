from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__, static_folder='../static', template_folder='../templates')
CORS(app)

# MongoDB connection
try:
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    client.server_info()
    db = client['webhookDB']
    collection = db['events']
except Exception as e:
    print("❌ MongoDB Connection Error:", e)
    collection = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def github_webhook():
    if collection is None:
        return "Database not connected", 500

    data = request.json
    event_type = request.headers.get('X-GitHub-Event')

    if event_type == "push":
        author = data.get('pusher', {}).get('name', 'Unknown')
        to_branch = data.get('ref', '').split('/')[-1]
        timestamp = datetime.utcnow().isoformat()

        event = {
            "author": author,
            "from_branch": None,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "event_type": "PUSH"
        }

    elif event_type == "pull_request":
        pr = data.get('pull_request', {})
        author = pr.get('user', {}).get('login', 'Unknown')
        from_branch = pr.get('head', {}).get('ref', '')
        to_branch = pr.get('base', {}).get('ref', '')
        timestamp = pr.get('created_at', datetime.utcnow().isoformat())

        event = {
            "author": author,
            "from_branch": from_branch,
            "to_branch": to_branch,
            "timestamp": timestamp,
            "event_type": "PULL_REQUEST"
        }

    else:
        return "Event type not handled", 200

    collection.insert_one(event)
    return "Webhook received", 200

@app.route('/events', methods=['GET'])
def get_events():
    if collection is None:
        return jsonify([])
    events = list(collection.find({}, {'_id': 0}).sort("timestamp", -1))
    return jsonify(events)

if __name__ == '__main__':
    app.run(debug=True)
