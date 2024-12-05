from app import db, app
from models import Notification
from datetime import datetime
import firebase_admin
from firebase_admin import messaging

def send_notification(user, message):
    try:
        notification = Notification(
            user_id=user.id,
            message=message,
            sent_at=datetime.utcnow(),
            status='pending'
        )
        db.session.add(notification)
        db.session.commit()

        if user.device_type == 'mobile' and user.fcm_token:
            send_fcm_notification(user.fcm_token, message)
            notification.status = 'sent'
        elif user.device_type == 'web':
            # Implement web push notification logic here
            notification.status = 'sent'
        else:
            notification.status = 'failed'
            app.logger.warning(f"Unsupported device type for user {user.id}")

        db.session.commit()
        return notification
    except Exception as e:
        app.logger.error(f"Error sending notification: {str(e)}")
        raise

def send_fcm_notification(fcm_token, message):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title='New Notification',
                body=message,
            ),
            token=fcm_token,
        )
        response = messaging.send(message)
        app.logger.info(f"Successfully sent FCM message: {response}")
    except Exception as e:
        app.logger.error(f"Error sending FCM notification: {str(e)}")
        raise