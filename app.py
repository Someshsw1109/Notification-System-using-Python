from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from logging.config import dictConfig
import firebase_admin
from firebase_admin import credentials, messaging
import os

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notifications.db'
db = SQLAlchemy(app)

# Initialize Firebase Admin SDK (optional)
if os.path.exists('firebase-adminsdk.json'):
    cred = credentials.Certificate('firebase-adminsdk.json')
    firebase_admin.initialize_app(cred)

from models import User, Notification
from notification_service import send_notification

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_notification', methods=['POST'])
def send_notification_route():
    try:
        data = request.json
        user_id = data.get('user_id')
        message = data.get('message')
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        notification = send_notification(user, message)
        return jsonify({'message': 'Notification sent successfully', 'notification_id': notification.id}), 200
    except Exception as e:
        app.logger.error(f"Error sending notification: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)