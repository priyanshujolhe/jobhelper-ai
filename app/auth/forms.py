from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, HiddenField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp


class RequestOTPForm(FlaskForm):
    email = StringField(
        "Email Address",
        validators=[
            DataRequired(message="Please provide an email address."),
            Email(message="Please enter a valid email address."),
            Length(max=255),
        ],
        render_kw={"placeholder": "name@example.com", "autocomplete": "email"},
    )
    submit = SubmitField("Send Verification Code")


class VerifyOTPForm(FlaskForm):
    email = HiddenField("Email", validators=[DataRequired()])
    otp_code = StringField(
        "6-Digit OTP Code",
        validators=[
            DataRequired(message="Enter the 6-digit verification code sent to your email."),
            Length(min=6, max=6, message="The code must be exactly 6 digits."),
            Regexp(r"^\d{6}$", message="Verification code must contain only numbers."),
        ],
        render_kw={"placeholder": "• • • • • •", "maxlength": "6", "autocomplete": "one-time-code"},
    )
    submit = SubmitField("Verify & Continue to Dashboard")


class CompleteProfileForm(FlaskForm):
    full_name = StringField(
        "Full Name",
        validators=[DataRequired(message="Please enter your full name."), Length(max=120)],
        render_kw={"placeholder": "e.g. John Doe"},
    )
    phone = StringField(
        "Phone Number",
        validators=[Length(max=40)],
        render_kw={"placeholder": "+1 (555) 000-0000"},
    )
    headline = StringField(
        "Professional Headline",
        validators=[Length(max=200)],
        render_kw={"placeholder": "e.g. Full Stack Developer | ML Enthusiast"},
    )
    location = StringField(
        "Location / City",
        validators=[Length(max=120)],
        render_kw={"placeholder": "e.g. San Francisco, CA or Remote"},
    )
    bio = TextAreaField(
        "Professional Bio",
        validators=[Length(max=1000)],
        render_kw={"rows": 4, "placeholder": "Brief introduction about your experience, interests, and career goals."},
    )
    submit = SubmitField("Save Profile & Access Dashboard")
