import smtplib
import secrets
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models import User, OTPVerification, UserProfile

logger = logging.getLogger(__name__)


def generate_otp() -> str:
    """Generate a cryptographically secure 6-digit numeric OTP."""
    # secrets.randbelow ensures uniform distribution [100000, 999999]
    return f"{secrets.randbelow(900000) + 100000}"


def is_smtp_configured() -> bool:
    """Check if SMTP credentials are provided in configuration."""
    cfg = current_app.config
    host = cfg.get("SMTP_HOST", "")
    username = cfg.get("SMTP_USERNAME", "")
    password = cfg.get("SMTP_PASSWORD", "")
    return bool(host and username and password)


def send_otp_email(to_email: str, otp_code: str) -> tuple[bool, str]:
    """
    Send real OTP email via configured SMTP server using responsive HTML template.
    Returns (success, message).
    """
    cfg = current_app.config

    if not is_smtp_configured():
        # When SMTP is not configured in .env, record to console and instance/dev_email_outbox.log
        # so local development, testing, and faculty demonstration work without being blocked
        import os
        instance_dir = os.path.join(current_app.root_path, "..", "instance")
        os.makedirs(instance_dir, exist_ok=True)
        log_path = os.path.join(instance_dir, "dev_email_outbox.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"[{timestamp}] To: {to_email} | OTP: {otp_code} (Valid for 5 mins)\n"
        )
        try:
            with open(log_path, "a") as f:
                f.write(log_entry)
        except Exception:
            pass

        print("\n" + "=" * 65)
        print(f"📧 [JOBHELPER LOCAL DEV OTP] Verification Code for: {to_email}")
        print(f"👉  {otp_code}  👈 (Expires in 5 minutes)")
        print(f"💡 (To deliver real emails to your inbox, add Gmail App Password to .env)")
        print("=" * 65 + "\n", flush=True)

        return (
            True,
            f"Code dispatched! (Development mode: Your code is {otp_code}. To send to your real inbox, add SMTP credentials to .env).",
        )

    host = cfg.get("SMTP_HOST")
    port = cfg.get("SMTP_PORT", 587)
    username = cfg.get("SMTP_USERNAME")
    password = cfg.get("SMTP_PASSWORD")
    use_tls = cfg.get("SMTP_USE_TLS", True)
    sender = cfg.get("MAIL_DEFAULT_SENDER", "JobHelper AI <noreply@jobhelper.local>")
    expiry_minutes = cfg.get("OTP_EXPIRY_MINUTES", 5)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Your JobHelper Verification Code: {otp_code}"
    msg["From"] = sender
    msg["To"] = to_email

    plain_text = f"""
Hello,

Your verification code for JobHelper AI is: {otp_code}

This code will expire in {expiry_minutes} minutes.

Security Notice:
- Do not share this code with anyone. JobHelper staff will never ask for your code.
- If you did not request this code, you can safely ignore this email.

Best regards,
The JobHelper AI Team
"""

    html_text = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Your JobHelper Verification Code</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background-color: #f8fafc;
      margin: 0;
      padding: 30px 10px;
      color: #1e293b;
    }}
    .email-container {{
      max-width: 520px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 12px;
      border: 1px solid #e2e8f0;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
      overflow: hidden;
    }}
    .header {{
      background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
      padding: 32px 24px;
      text-align: center;
      color: #ffffff;
    }}
    .brand {{
      font-size: 24px;
      font-weight: 700;
      letter-spacing: -0.5px;
    }}
    .brand span {{
      color: #38bdf8;
    }}
    .subtitle {{
      font-size: 13px;
      color: #94a3b8;
      margin-top: 4px;
    }}
    .content {{
      padding: 32px 28px;
    }}
    .otp-box {{
      background: #f0fdf4;
      border: 2px dashed #22c55e;
      border-radius: 10px;
      padding: 20px;
      text-align: center;
      margin: 24px 0;
    }}
    .otp-code {{
      font-size: 36px;
      font-weight: 800;
      letter-spacing: 8px;
      color: #15803d;
      font-family: 'Courier New', Courier, monospace;
    }}
    .expiry {{
      font-size: 13px;
      color: #64748b;
      margin-top: 8px;
    }}
    .warning {{
      background: #fef2f2;
      border-left: 4px solid #ef4444;
      padding: 12px 16px;
      border-radius: 4px;
      font-size: 13px;
      color: #991b1b;
      margin: 20px 0;
    }}
    .footer {{
      border-top: 1px solid #e2e8f0;
      padding: 20px 24px;
      font-size: 12px;
      color: #94a3b8;
      text-align: center;
      background: #f8fafc;
    }}
  </style>
</head>
<body>
  <div class="email-container">
    <div class="header">
      <div class="brand">Job<span>Helper</span></div>
      <div class="subtitle">AI Resume Analyzer & Job Matcher</div>
    </div>
    <div class="content">
      <h2 style="font-size: 20px; font-weight: 600; margin-top: 0; color: #0f172a;">Verify Your Email Address</h2>
      <p style="font-size: 14px; line-height: 1.6; color: #475569;">
        You requested a one-time verification code to sign in to your <strong>JobHelper</strong> account. Enter the 6-digit code below to proceed:
      </p>
      
      <div class="otp-box">
        <div class="otp-code">{otp_code}</div>
        <div class="expiry">Expires in <strong>{expiry_minutes} minutes</strong></div>
      </div>

      <div class="warning">
        <strong>Security Notice:</strong> Never share this code with anyone. Our team will never ask for your verification code.
      </div>

      <p style="font-size: 13px; color: #64748b; line-height: 1.5;">
        If you did not request this login attempt, someone may have entered your email by mistake. You can safely disregard this message.
      </p>
    </div>
    <div class="footer">
      &copy; {datetime.now().year} JobHelper AI. Built for Smart Academic & Career Success.<br>
      This is an automated security transmission.
    </div>
  </div>
</body>
</html>
"""

    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_text, "html"))

    try:
        if port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=12)
        else:
            server = smtplib.SMTP(host, port, timeout=12)
            if use_tls:
                server.starttls()

        server.login(username, password)
        server.send_message(msg)
        server.quit()
        logger.info(f"OTP successfully emailed to {to_email}")
        return True, "Verification code sent to your email inbox."
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Auth error: {e}")
        return False, "SMTP Authentication failed. Please verify your SMTP username and App Password."
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False, f"Could not send email: {str(e)}"


def request_otp(email: str) -> tuple[bool, str]:
    """
    Validates email, enforces cooldown and rate limits, generates secure hashed OTP,
    and sends it to the recipient's email address.
    """
    clean_email = email.strip().lower()
    if not clean_email or "@" not in clean_email:
        return False, "Please enter a valid email address."

    now = datetime.now(timezone.utc)
    cooldown_seconds = current_app.config.get("OTP_RESEND_COOLDOWN_SECONDS", 60)
    expiry_minutes = current_app.config.get("OTP_EXPIRY_MINUTES", 5)

    # Check for active recent OTP to enforce 60s resend cooldown
    latest_otp = (
        OTPVerification.query.filter_by(email=clean_email, used=False)
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if latest_otp and not latest_otp.can_resend():
        # Calculate remaining seconds
        resend_time = latest_otp.resend_available_at
        if resend_time.tzinfo is None:
            resend_time = resend_time.replace(tzinfo=timezone.utc)
        remaining = max(1, int((resend_time - now).total_seconds()))
        return False, f"Please wait {remaining} seconds before requesting a new verification code."

    # Invalidate any existing unused OTPs for this email
    active_otps = OTPVerification.query.filter_by(email=clean_email, used=False).all()
    for o in active_otps:
        o.used = True

    # Find or create user
    user = User.query.filter_by(email=clean_email).first()
    if not user:
        user = User(email=clean_email, email_verified=False)
        db.session.add(user)
        db.session.flush()

    # Generate 6-digit OTP and secure hash
    raw_otp = generate_otp()
    otp_hash = generate_password_hash(raw_otp)

    expires_at = now + timedelta(minutes=expiry_minutes)
    resend_available_at = now + timedelta(seconds=cooldown_seconds)

    record = OTPVerification(
        user_id=user.id,
        email=clean_email,
        otp_hash=otp_hash,
        expires_at=expires_at,
        attempts=0,
        resend_available_at=resend_available_at,
        used=False,
    )
    db.session.add(record)
    db.session.commit()

    # Send email
    success, msg = send_otp_email(clean_email, raw_otp)
    if not success:
        # If sending failed, delete/invalidate OTP so user isn't stuck
        record.used = True
        db.session.commit()
        return False, msg

    return True, f"A 6-digit verification code has been dispatched to {clean_email}."


def verify_otp(email: str, entered_otp: str) -> tuple[bool, str, User or None]:
    """
    Verify user-provided OTP code securely.
    Returns (success, message, user_object).
    """
    clean_email = email.strip().lower()
    code = entered_otp.strip()

    if not code or len(code) != 6 or not code.isdigit():
        return False, "Please enter a valid 6-digit numeric verification code.", None

    record = (
        OTPVerification.query.filter_by(email=clean_email, used=False)
        .order_by(OTPVerification.created_at.desc())
        .first()
    )

    if not record:
        return False, "No active verification code found for this email. Please request a new one.", None

    if record.is_expired():
        record.used = True
        db.session.commit()
        return False, "This verification code has expired. Please request a new code.", None

    max_attempts = current_app.config.get("OTP_MAX_ATTEMPTS", 5)
    if record.attempts >= max_attempts:
        record.used = True
        db.session.commit()
        return False, "Maximum verification attempts exceeded. Code has been invalidated. Please request a new code.", None

    # Check hashed OTP
    if check_password_hash(record.otp_hash, code):
        record.used = True
        user = User.query.filter_by(email=clean_email).first()
        if user:
            user.email_verified = True
            if not user.profile:
                profile = UserProfile(user_id=user.id, full_name=user.name or "")
                db.session.add(profile)
        db.session.commit()
        return True, "Verification successful! Welcome to JobHelper.", user
    else:
        record.attempts += 1
        db.session.commit()
        remaining = max_attempts - record.attempts
        if remaining <= 0:
            record.used = True
            db.session.commit()
            return False, "Invalid code. Maximum attempts reached. Please request a new code.", None
        return False, f"Invalid code. You have {remaining} attempt(s) remaining.", None
