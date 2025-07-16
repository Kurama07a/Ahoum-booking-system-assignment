import requests
import json
from datetime import datetime, timedelta

# Test email service
EMAIL_SERVICE_URL = "http://localhost:5003"

def test_email_service():
    """Test the email service with sample data"""
    
    # Sample booking data
    booking_data = {
        "booking_id": "test-123",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "name": "John Doe"
        },
        "session": {
            "id": 1,
            "title": "Morning Meditation",
            "session_type": "session",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=1)).isoformat(),
            "price": 25.0
        },
        "facilitator": {
            "id": 1,
            "email": "facilitator@example.com",
            "name": "Jane Smith"
        }
    }
    
    print("🧪 Testing Email Service")
    print("=" * 50)
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{EMAIL_SERVICE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test sending both emails
    print("\n2. Testing booking email sending...")
    try:
        response = requests.post(
            f"{EMAIL_SERVICE_URL}/send-booking-emails",
            json=booking_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Booking emails sent successfully")
            print(f"Response: {response.json()}")
        elif response.status_code == 207:
            print("⚠️  Partial success - some emails sent")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Email sending failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Email sending error: {e}")
        return False
    
    # Test individual email endpoints
    print("\n3. Testing individual email endpoints...")
    
    # Test user confirmation
    try:
        response = requests.post(
            f"{EMAIL_SERVICE_URL}/send-booking-confirmation",
            json=booking_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ User confirmation email sent")
        else:
            print(f"❌ User confirmation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ User confirmation error: {e}")
    
    # Test facilitator notification
    try:
        response = requests.post(
            f"{EMAIL_SERVICE_URL}/send-facilitator-notification",
            json=booking_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Facilitator notification email sent")
        else:
            print(f"❌ Facilitator notification failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Facilitator notification error: {e}")
    
    print("\n🎉 Email service test completed!")
    print("\nNote: Check the email addresses specified in the test data to see if emails were received.")
    print("Make sure your SMTP settings are correctly configured in the .env file.")
    
    return True

if __name__ == "__main__":
    test_email_service()
