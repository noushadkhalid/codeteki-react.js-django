import io
import base64
import time

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

import qrcode
import qrcode.image.svg

from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
from django_otp import login as otp_login


def _otp_login_with_timestamp(request, device):
    """Call otp_login and stamp the session so the middleware can enforce TTL."""
    otp_login(request, device)
    request.session["otp_verified_at"] = time.time()


def _get_next_url(request):
    """Return the URL the user was trying to reach before OTP, or /admin/."""
    return request.session.pop("admin_otp_next", "/admin/")


def _generate_qr_svg(device):
    """Return an inline SVG string for the TOTP provisioning URI."""
    uri = device.config_url
    img = qrcode.make(uri, image_factory=qrcode.image.svg.SvgPathImage)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode("utf-8")


# ---------------------------------------------------------------------------
# Verify view — shown when user has a confirmed TOTP device
# ---------------------------------------------------------------------------
@login_required(login_url="/admin/login/")
@staff_member_required(login_url="/admin/login/")
@require_http_methods(["GET", "POST"])
def otp_verify_view(request):
    if request.user.is_verified():
        return redirect(_get_next_url(request))

    error = None

    if request.method == "POST":
        token = request.POST.get("token", "").strip()

        if not token:
            error = "Please enter a verification code."
        else:
            # Try TOTP devices first.
            for device in TOTPDevice.objects.filter(user=request.user, confirmed=True):
                if device.verify_token(token):
                    _otp_login_with_timestamp(request, device)
                    return redirect(_get_next_url(request))

            # Fall back to static (backup) devices.
            for device in StaticDevice.objects.filter(user=request.user, confirmed=True):
                if device.verify_token(token):
                    _otp_login_with_timestamp(request, device)
                    return redirect(_get_next_url(request))

            error = "Invalid code. Please try again."

    return render(request, "admin/otp/verify.html", {"error": error})


# ---------------------------------------------------------------------------
# Setup view — shown when user has no confirmed TOTP device
# ---------------------------------------------------------------------------
@login_required(login_url="/admin/login/")
@staff_member_required(login_url="/admin/login/")
@require_http_methods(["GET", "POST"])
def otp_setup_view(request):
    if request.user.is_verified():
        return redirect(_get_next_url(request))

    # Re-use an unconfirmed device if one already exists (e.g. user refreshed
    # the setup page), otherwise create a new one.
    device = TOTPDevice.objects.filter(user=request.user, confirmed=False).first()
    if device is None:
        device = TOTPDevice.objects.create(
            user=request.user,
            name="default",
            confirmed=False,
        )

    qr_svg = _generate_qr_svg(device)
    secret_key = base64.b32encode(device.bin_key).decode("utf-8")
    error = None

    if request.method == "POST":
        token = request.POST.get("token", "").strip()

        if not token:
            error = "Please enter the code from your authenticator app."
        elif device.verify_token(token):
            # Token is valid — mark device as confirmed.
            device.confirmed = True
            device.save()
            _otp_login_with_timestamp(request, device)

            # Generate backup codes.
            static_device, _ = StaticDevice.objects.get_or_create(
                user=request.user,
                name="backup",
                defaults={"confirmed": True},
            )
            # Clear any old tokens and generate fresh ones.
            static_device.token_set.all().delete()
            backup_codes = []
            for _ in range(10):
                token_str = StaticToken.random_token()
                static_device.token_set.create(token=token_str)
                backup_codes.append(token_str)

            request.session["otp_backup_codes"] = backup_codes
            return redirect("admin_otp_setup_complete")
        else:
            error = "Invalid code. Make sure your authenticator app is showing the latest code."

    return render(request, "admin/otp/setup.html", {
        "qr_svg": qr_svg,
        "secret_key": secret_key,
        "error": error,
    })


# ---------------------------------------------------------------------------
# Setup complete — show backup codes once
# ---------------------------------------------------------------------------
@login_required(login_url="/admin/login/")
@staff_member_required(login_url="/admin/login/")
def otp_setup_complete_view(request):
    backup_codes = request.session.pop("otp_backup_codes", None)

    if not backup_codes:
        return redirect("/admin/")

    return render(request, "admin/otp/setup_complete.html", {
        "backup_codes": backup_codes,
    })
