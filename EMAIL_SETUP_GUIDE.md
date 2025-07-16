# Email Configuration Guide

## Gmail Setup (Recommended)
1. Enable 2-Factor Authentication:
   - Go to https://myaccount.google.com/
   - Security → 2-Step Verification → Turn On

2. Create App Password:
   - Security → App passwords
   - Select "Mail" → Generate
   - Use the 16-character password (remove spaces)

EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-16-character-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

## Outlook/Hotmail Setup
EMAIL_ADDRESS=your-email@outlook.com
EMAIL_PASSWORD=your-regular-password
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587

## Yahoo Mail Setup
EMAIL_ADDRESS=your-email@yahoo.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587

Note: Yahoo also requires app passwords for third-party apps

## Custom SMTP Server
EMAIL_ADDRESS=your-email@yourdomain.com
EMAIL_PASSWORD=your-password
SMTP_SERVER=mail.yourdomain.com
SMTP_PORT=587

## Common Issues:
1. "Authentication failed" - Check app password, not regular password
2. "Connection refused" - Verify SMTP server and port
3. "Less secure app access" - Use app passwords instead

## Security Tips:
- Never use your regular email password
- Always use app passwords for Gmail/Yahoo
- Keep credentials in .env file (never commit to git)
- Use strong, unique passwords
