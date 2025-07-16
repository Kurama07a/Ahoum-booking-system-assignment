from flask import Flask, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import logging

app = Flask(__name__)

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS', 'your-email@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'your-app-password')
EMAIL_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'Booking System')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = SMTP_SERVER
        self.smtp_port = SMTP_PORT
        self.email_address = EMAIL_ADDRESS
        self.email_password = EMAIL_PASSWORD
        self.from_name = EMAIL_FROM_NAME

    def send_email(self, to_email, subject, html_content, text_content=None):
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.email_address}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Connect to server and send email
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def generate_booking_confirmation_email(self, booking_data):
        """Generate booking confirmation email for user"""
        user_name = booking_data.get('user', {}).get('name', 'User')
        session_title = booking_data.get('session', {}).get('title', 'Session')
        session_type = booking_data.get('session', {}).get('session_type', 'session')
        start_time = booking_data.get('session', {}).get('start_time', '')
        end_time = booking_data.get('session', {}).get('end_time', '')
        facilitator_name = booking_data.get('facilitator', {}).get('name', 'Facilitator')
        price = booking_data.get('session', {}).get('price', 0)
        booking_id = booking_data.get('booking_id', '')

        # Format dates
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            formatted_start = start_dt.strftime('%B %d, %Y at %I:%M %p')
            formatted_end = end_dt.strftime('%I:%M %p')
        except:
            formatted_start = start_time
            formatted_end = end_time

        subject = f"Booking Confirmation - {session_title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }}
                .button {{ background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Booking Confirmed!</h1>
            </div>
            <div class="content">
                <h2>Hello {user_name},</h2>
                <p>Your booking has been confirmed! Here are the details:</p>
                
                <div class="booking-details">
                    <h3>Booking Details</h3>
                    <p><strong>Session:</strong> {session_title}</p>
                    <p><strong>Type:</strong> {session_type.title()}</p>
                    <p><strong>Date & Time:</strong> {formatted_start} - {formatted_end}</p>
                    <p><strong>Facilitator:</strong> {facilitator_name}</p>
                    <p><strong>Price:</strong> ${price:.2f}</p>
                    <p><strong>Booking ID:</strong> {booking_id}</p>
                </div>

                <p>We're excited to have you join us! Please arrive 10 minutes early to get settled.</p>
                
                <p>If you have any questions or need to make changes to your booking, please contact us.</p>
                
                <p>Best regards,<br>The Booking System Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply directly to this email.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Booking Confirmed!

        Hello {user_name},

        Your booking has been confirmed! Here are the details:

        Session: {session_title}
        Type: {session_type.title()}
        Date & Time: {formatted_start} - {formatted_end}
        Facilitator: {facilitator_name}
        Price: ${price:.2f}
        Booking ID: {booking_id}

        We're excited to have you join us! Please arrive 10 minutes early to get settled.

        If you have any questions or need to make changes to your booking, please contact us.

        Best regards,
        The Booking System Team
        """

        return subject, html_content, text_content

    def generate_facilitator_notification_email(self, booking_data):
        """Generate booking notification email for facilitator"""
        facilitator_name = booking_data.get('facilitator', {}).get('name', 'Facilitator')
        user_name = booking_data.get('user', {}).get('name', 'User')
        user_email = booking_data.get('user', {}).get('email', '')
        session_title = booking_data.get('session', {}).get('title', 'Session')
        session_type = booking_data.get('session', {}).get('session_type', 'session')
        start_time = booking_data.get('session', {}).get('start_time', '')
        end_time = booking_data.get('session', {}).get('end_time', '')
        price = booking_data.get('session', {}).get('price', 0)
        booking_id = booking_data.get('booking_id', '')

        # Format dates
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            formatted_start = start_dt.strftime('%B %d, %Y at %I:%M %p')
            formatted_end = end_dt.strftime('%I:%M %p')
        except:
            formatted_start = start_time
            formatted_end = end_time

        subject = f"New Booking - {session_title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #059669; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; }}
                .booking-details {{ background-color: #f0f9ff; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .footer {{ background-color: #f1f1f1; padding: 15px; text-align: center; font-size: 12px; }}
                .highlight {{ background-color: #fef3c7; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>New Booking Received!</h1>
            </div>
            <div class="content">
                <h2>Hello {facilitator_name},</h2>
                <p>You have received a new booking for your session!</p>
                
                <div class="booking-details">
                    <h3>Booking Details</h3>
                    <p><strong>Session:</strong> {session_title}</p>
                    <p><strong>Type:</strong> {session_type.title()}</p>
                    <p><strong>Date & Time:</strong> {formatted_start} - {formatted_end}</p>
                    <p><strong>Revenue:</strong> ${price:.2f}</p>
                    <p><strong>Booking ID:</strong> {booking_id}</p>
                </div>

                <div class="highlight">
                    <h3>Participant Information</h3>
                    <p><strong>Name:</strong> {user_name}</p>
                    <p><strong>Email:</strong> {user_email}</p>
                </div>

                <p>The participant will receive a confirmation email with session details.</p>
                
                <p>You can manage your bookings and sessions from your facilitator dashboard.</p>
                
                <p>Best regards,<br>The Booking System Team</p>
            </div>
            <div class="footer">
                <p>This is an automated email. Please do not reply directly to this email.</p>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        New Booking Received!

        Hello {facilitator_name},

        You have received a new booking for your session!

        Booking Details:
        Session: {session_title}
        Type: {session_type.title()}
        Date & Time: {formatted_start} - {formatted_end}
        Revenue: ${price:.2f}
        Booking ID: {booking_id}

        Participant Information:
        Name: {user_name}
        Email: {user_email}

        The participant will receive a confirmation email with session details.

        You can manage your bookings and sessions from your facilitator dashboard.

        Best regards,
        The Booking System Team
        """

        return subject, html_content, text_content

# Initialize email service
email_service = EmailService()

@app.route('/send-booking-confirmation', methods=['POST'])
def send_booking_confirmation():
    """Send booking confirmation email to user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user', 'session', 'facilitator', 'booking_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        user_email = data['user'].get('email')
        if not user_email:
            return jsonify({'error': 'User email is required'}), 400

        # Generate and send email
        subject, html_content, text_content = email_service.generate_booking_confirmation_email(data)
        
        success = email_service.send_email(
            to_email=user_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

        if success:
            return jsonify({'message': 'Booking confirmation email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send booking confirmation email'}), 500

    except Exception as e:
        logger.error(f"Error sending booking confirmation: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/send-facilitator-notification', methods=['POST'])
def send_facilitator_notification():
    """Send booking notification email to facilitator"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user', 'session', 'facilitator', 'booking_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        facilitator_email = data['facilitator'].get('email')
        if not facilitator_email:
            return jsonify({'error': 'Facilitator email is required'}), 400

        # Generate and send email
        subject, html_content, text_content = email_service.generate_facilitator_notification_email(data)
        
        success = email_service.send_email(
            to_email=facilitator_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

        if success:
            return jsonify({'message': 'Facilitator notification email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send facilitator notification email'}), 500

    except Exception as e:
        logger.error(f"Error sending facilitator notification: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/send-booking-emails', methods=['POST'])
def send_booking_emails():
    """Send both booking confirmation and facilitator notification emails"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['user', 'session', 'facilitator', 'booking_id']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        user_email = data['user'].get('email')
        facilitator_email = data['facilitator'].get('email')
        
        if not user_email or not facilitator_email:
            return jsonify({'error': 'Both user and facilitator emails are required'}), 400

        results = {'user_email': False, 'facilitator_email': False}

        # Send booking confirmation to user
        try:
            subject, html_content, text_content = email_service.generate_booking_confirmation_email(data)
            results['user_email'] = email_service.send_email(
                to_email=user_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
        except Exception as e:
            logger.error(f"Error sending user confirmation: {str(e)}")

        # Send notification to facilitator
        try:
            subject, html_content, text_content = email_service.generate_facilitator_notification_email(data)
            results['facilitator_email'] = email_service.send_email(
                to_email=facilitator_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
        except Exception as e:
            logger.error(f"Error sending facilitator notification: {str(e)}")

        if results['user_email'] and results['facilitator_email']:
            return jsonify({'message': 'Both emails sent successfully', 'results': results}), 200
        elif results['user_email'] or results['facilitator_email']:
            return jsonify({'message': 'Partial success - some emails sent', 'results': results}), 207
        else:
            return jsonify({'error': 'Failed to send both emails', 'results': results}), 500

    except Exception as e:
        logger.error(f"Error sending booking emails: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'email_service',
        'timestamp': datetime.utcnow().isoformat(),
        'smtp_server': SMTP_SERVER,
        'smtp_port': SMTP_PORT
    }), 200

if __name__ == '__main__':
    app.run(debug=True, port=5003, host='0.0.0.0')
