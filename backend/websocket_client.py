import socketio
import logging
import threading
import time
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationWebSocketClient:
    def __init__(self, notification_service_url=None, token=None):
        self.notification_service_url = notification_service_url or os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5002')
        self.token = token or os.getenv('BACKEND_SERVICE_TOKEN', 'backend-service-token-here')
        self.sio = socketio.Client(logger=True, engineio_logger=True)
        self.connected = False
        self.setup_event_handlers()
        
    def setup_event_handlers(self):
        @self.sio.event
        def connect():
            logger.info("Connected to notification service")
            # Authenticate as backend service
            self.sio.emit('backend_connect', {'token': self.token})
        
        @self.sio.event
        def disconnect():
            logger.info("Disconnected from notification service")
            self.connected = False
        
        @self.sio.event
        def backend_auth_success(data):
            logger.info("Backend authentication successful")
            self.connected = True
        
        @self.sio.event
        def auth_error(data):
            logger.error(f"Authentication error: {data.get('error')}")
            self.connected = False
        
        @self.sio.event
        def notification_delivered(data):
            logger.info(f"Notification delivered: {data}")
        
        @self.sio.event
        def notification_stored(data):
            logger.info(f"Notification stored for offline facilitator: {data}")
        
        @self.sio.event
        def notification_error(data):
            logger.error(f"Notification error: {data.get('error')}")
    
    def connect_to_service(self):
        """Connect to the notification service"""
        try:
            self.sio.connect(self.notification_service_url)
            # Wait a bit for authentication
            time.sleep(1)
            return self.connected
        except Exception as e:
            logger.error(f"Failed to connect to notification service: {e}")
            return False
    
    def disconnect_from_service(self):
        """Disconnect from the notification service"""
        if self.sio.connected:
            self.sio.disconnect()
    
    def send_booking_notification(self, booking_data):
        """Send booking notification via WebSocket"""
        if not self.connected:
            logger.warning("Not connected to notification service, attempting to reconnect...")
            if not self.connect_to_service():
                logger.error("Failed to connect to notification service")
                return False
        
        try:
            self.sio.emit('booking_notification', booking_data)
            logger.info(f"Booking notification sent: {booking_data['booking_id']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send booking notification: {e}")
            return False
    
    def is_connected(self):
        """Check if connected to notification service"""
        return self.connected and self.sio.connected

# Global instance
notification_client = NotificationWebSocketClient()

def initialize_notification_client():
    """Initialize the notification client connection"""
    success = notification_client.connect_to_service()
    if success:
        logger.info("Notification client initialized successfully")
    else:
        logger.error("Failed to initialize notification client")
    return success

def send_booking_notification(booking_data):
    """Send booking notification through WebSocket"""
    return notification_client.send_booking_notification(booking_data)

def cleanup_notification_client():
    """Cleanup notification client connection"""
    notification_client.disconnect_from_service()
