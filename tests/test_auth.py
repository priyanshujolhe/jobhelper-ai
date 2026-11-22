import pytest
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app
from app.extensions import db
from app.models import User, OTPVerification
from app.auth.services import generate_otp, verify_otp


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_otp_generation():
    """Verify OTP generation produces a 6-digit numeric string."""
    for _ in range(50):
        otp = generate_otp()
        assert len(otp) == 6
        assert otp.isdigit()
        assert 100000 <= int(otp) <= 999999


def test_otp_hashing():
    """Verify PBKDF2 salted hash is used and never stored as plaintext."""
    raw_otp = "849201"
    hashed = generate_password_hash(raw_otp)
    assert hashed != raw_otp
    assert check_password_hash(hashed, raw_otp)
    assert not check_password_hash(hashed, "123456")


def test_otp_verification_success(app):
    """Test successful OTP verification flow."""
    with app.app_context():
        email = "candidate@example.com"
        raw_code = "654321"
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=5)
        resend_time = now + timedelta(seconds=60)

        user = User(email=email, email_verified=False)
        db.session.add(user)
        db.session.flush()

        otp_rec = OTPVerification(
            user_id=user.id,
            email=email,
            otp_hash=generate_password_hash(raw_code),
            expires_at=expires,
            attempts=0,
            resend_available_at=resend_time,
            used=False,
        )
        db.session.add(otp_rec)
        db.session.commit()

        success, msg, verified_user = verify_otp(email, raw_code)
        assert success is True
        assert verified_user is not None
        assert verified_user.email_verified is True
        assert otp_rec.used is True


def test_otp_invalid_code(app):
    """Test entering invalid OTP decrements remaining attempts."""
    with app.app_context():
        email = "test@example.com"
        raw_code = "112233"
        now = datetime.now(timezone.utc)
        otp_rec = OTPVerification(
            email=email,
            otp_hash=generate_password_hash(raw_code),
            expires_at=now + timedelta(minutes=5),
            attempts=0,
            resend_available_at=now + timedelta(seconds=60),
            used=False,
        )
        db.session.add(otp_rec)
        db.session.commit()

        success, msg, user = verify_otp(email, "999999")
        assert success is False
        assert "attempt(s) remaining" in msg
        assert otp_rec.attempts == 1
        assert otp_rec.used is False


def test_otp_expiration(app):
    """Test expired OTP rejection."""
    with app.app_context():
        email = "expired@example.com"
        raw_code = "778899"
        past_time = datetime.now(timezone.utc) - timedelta(minutes=10)
        otp_rec = OTPVerification(
            email=email,
            otp_hash=generate_password_hash(raw_code),
            expires_at=past_time,
            attempts=0,
            resend_available_at=past_time,
            used=False,
        )
        db.session.add(otp_rec)
        db.session.commit()

        success, msg, user = verify_otp(email, raw_code)
        assert success is False
        assert "expired" in msg.lower()
        assert otp_rec.used is True


def test_otp_reuse_prevention(app):
    """Test OTP cannot be reused once verified."""
    with app.app_context():
        email = "reuse@example.com"
        raw_code = "554433"
        now = datetime.now(timezone.utc)

        user = User(email=email, email_verified=False)
        db.session.add(user)
        db.session.flush()

        otp_rec = OTPVerification(
            user_id=user.id,
            email=email,
            otp_hash=generate_password_hash(raw_code),
            expires_at=now + timedelta(minutes=5),
            attempts=0,
            resend_available_at=now + timedelta(seconds=60),
            used=False,
        )
        db.session.add(otp_rec)
        db.session.commit()

        # First verification succeeds
        success1, _, _ = verify_otp(email, raw_code)
        assert success1 is True

        # Second verification of same code fails
        success2, msg2, _ = verify_otp(email, raw_code)
        assert success2 is False
        assert "no active verification code" in msg2.lower()
