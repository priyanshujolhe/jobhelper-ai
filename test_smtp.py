#!/usr/bin/env python3
"""
JobHelper AI - SMTP Email Diagnostic Tool
Use this script to test and verify your real email delivery setup.
"""
import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

basedir = Path(__file__).resolve().parent
load_dotenv(basedir / ".env")

host = os.getenv("SMTP_HOST", "").strip()
port = int(os.getenv("SMTP_PORT", 587))
username = os.getenv("SMTP_USERNAME", "").strip()
password = os.getenv("SMTP_PASSWORD", "").strip()
sender = os.getenv("MAIL_DEFAULT_SENDER", username)

print("\n" + "=" * 60)
print("📧 JobHelper AI — Real Email Delivery Diagnostic")
print("=" * 60)

if not host or not username or not password:
    print("\n❌ Incomplete SMTP Configuration in .env:")
    print(f"   SMTP_HOST:     '{host or '<NOT SET>'}'")
    print(f"   SMTP_PORT:     {port}")
    print(f"   SMTP_USERNAME: '{username or '<NOT SET>'}'")
    print(f"   SMTP_PASSWORD: '{'********' if password else '<NOT SET>'}'")
    print("\n👉 To send real emails, update your .env file with:")
    print("   SMTP_HOST=smtp.gmail.com")
    print("   SMTP_PORT=587")
    print("   SMTP_USERNAME=your_email@gmail.com")
    print("   SMTP_PASSWORD=your_16_digit_app_password")
    print("   MAIL_DEFAULT_SENDER=JobHelper AI <your_email@gmail.com>\n")
    sys.exit(1)

test_recipient = sys.argv[1] if len(sys.argv) > 1 else username

print(f"\nConnecting to SMTP Server: {host}:{port} ...")
print(f"Authenticating as: {username} ...")
print(f"Sending test email to: {test_recipient} ...")

msg = MIMEMultipart("alternative")
msg["Subject"] = "JobHelper AI — Real Email Delivery Test"
msg["From"] = sender
msg["To"] = test_recipient

html_content = """
<div style="font-family: Arial, sans-serif; padding: 20px; border: 1px solid #e2e8f0; border-radius: 8px;">
    <h2 style="color: #2563eb;">JobHelper AI — Email Test Successful!</h2>
    <p>Your SMTP mail configuration is working perfectly.</p>
    <p>Real 6-digit OTP verification codes will now be delivered to your inbox.</p>
</div>
"""
msg.attach(MIMEText("JobHelper AI — Email Test Successful! Your SMTP configuration is working.", "plain"))
msg.attach(MIMEText(html_content, "html"))

try:
    if port == 465:
        server = smtplib.SMTP_SSL(host, port, timeout=12)
    else:
        server = smtplib.SMTP(host, port, timeout=12)
        server.starttls()

    server.login(username, password)
    server.send_message(msg)
    server.quit()
    print("\n✅ SUCCESS! Test email was delivered successfully!")
    print(f"📬 Check your inbox at: {test_recipient}\n")
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ Authentication Failed: {e}")
    print("💡 If using Gmail, make sure you generated a 16-character 'App Password' from Google Account -> Security -> 2-Step Verification.")
except Exception as e:
    print(f"\n❌ Connection Error: {e}")
