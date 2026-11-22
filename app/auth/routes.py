from flask import render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.auth.forms import RequestOTPForm, VerifyOTPForm, CompleteProfileForm
from app.auth.services import request_otp, verify_otp, is_smtp_configured
from app.extensions import db
from app.models import UserProfile


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RequestOTPForm()
    smtp_ready = is_smtp_configured()

    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        success, message = request_otp(email)
        if success:
            session["pending_otp_email"] = email
            flash(message, "success")
            return redirect(url_for("auth.verify_otp"))
        else:
            flash(message, "danger")

    return render_template("auth/login.html", form=form, smtp_ready=smtp_ready)


@auth_bp.route("/verify-otp", methods=["GET", "POST"], endpoint="verify_otp")
@auth_bp.route("/verify-otp", methods=["GET", "POST"], endpoint="verify_otp_route")
def verify_otp_route():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    pending_email = session.get("pending_otp_email")
    if not pending_email:
        flash("Please enter your email address to receive a verification code.", "warning")
        return redirect(url_for("auth.login"))

    form = VerifyOTPForm()
    form.email.data = pending_email

    if form.validate_on_submit():
        entered_code = form.otp_code.data.strip()
        success, message, user = verify_otp(pending_email, entered_code)
        if success and user:
            login_user(user, remember=True)
            session.pop("pending_otp_email", None)
            flash(message, "success")

            # If user has no name yet, prompt to complete profile
            if not user.name:
                return redirect(url_for("auth.complete_profile"))
            return redirect(url_for("dashboard.index"))
        else:
            flash(message, "danger")

    return render_template("auth/verify_otp.html", form=form, email=pending_email)


@auth_bp.route("/resend-otp", methods=["POST"])
def resend_otp():
    pending_email = session.get("pending_otp_email")
    if not pending_email:
        flash("Session expired. Please enter your email again.", "warning")
        return redirect(url_for("auth.login"))

    success, message = request_otp(pending_email)
    if success:
        flash(f"A new verification code was sent to {pending_email}.", "success")
    else:
        flash(message, "danger")

    return redirect(url_for("auth.verify_otp"))


@auth_bp.route("/complete-profile", methods=["GET", "POST"])
@login_required
def complete_profile():
    form = CompleteProfileForm()

    profile = current_user.profile
    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    if form.validate_on_submit():
        current_user.name = form.full_name.data.strip()
        profile.full_name = form.full_name.data.strip()
        profile.phone = form.phone.data.strip() if form.phone.data else None
        profile.headline = form.headline.data.strip() if form.headline.data else None
        profile.location = form.location.data.strip() if form.location.data else None
        profile.bio = form.bio.data.strip() if form.bio.data else None
        db.session.commit()

        flash("Profile updated successfully! Welcome to your JobHelper Dashboard.", "success")
        return redirect(url_for("dashboard.index"))
    elif request.method == "GET":
        form.full_name.data = current_user.name or profile.full_name or ""
        form.phone.data = profile.phone or ""
        form.headline.data = profile.headline or ""
        form.location.data = profile.location or ""
        form.bio.data = profile.bio or ""

    return render_template("auth/complete_profile.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been signed out successfully.", "info")
    return redirect(url_for("auth.login"))
