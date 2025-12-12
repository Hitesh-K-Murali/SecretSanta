#!/usr/bin/env python3
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Gmail App Password (spaces removed)
sender_email = "reach.out.hiteshkmurali@gmail.com"
sender_password = "vaunldccinpbkkke"
recipient_email = "hitesh.gen9@gmail.com"

print("Testing Gmail with App Password...")
print(f"From: {sender_email}")
print(f"To: {recipient_email}")

try:
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "🎅 Secret Santa - Email System Working!"
    
    body = """
Ho Ho Ho! 🎄

SUCCESS! Your Secret Santa email system is now working!

This confirms:
✅ Gmail App Password is valid
✅ SMTP_SSL connection successful
✅ Emails can now be sent from your application

The confirmation emails will now be sent to users when they register!

Time: 2025-12-11 11:40
Method: SMTP_SSL (port 465)

Merry Christmas! 🎁
- The Secret Santa Bot 🤖
    """
    msg.attach(MIMEText(body, 'plain'))
    
    # Connect using SMTP_SSL with custom context
    print("\nConnecting to smtp.gmail.com:465...")
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=context)
    
    print("Logging in...")
    server.login(sender_email, sender_password)
    
    print("Sending email...")
    server.sendmail(sender_email, recipient_email, msg.as_string())
    
    print("Closing connection...")
    server.quit()
    
    print("\n" + "="*60)
    print("✓ SUCCESS! Email sent to hitesh.gen9@gmail.com")
    print("="*60)
    print("\nPlease check your inbox (and spam folder)!")
    
except Exception as e:
    print(f"\n✗ FAILED! Error: {str(e)}")
    import traceback
    traceback.print_exc()
