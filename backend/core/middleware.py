import time

from django.shortcuts import redirect

# OTP verification expires after 24 hours (in seconds).
OTP_VERIFY_TTL = 24 * 60 * 60


def is_otp_verified(request):
    """Check if the user has a fresh OTP verification (within 24 hours).

    Used by both the middleware and OTP views to avoid inconsistent checks.
    """
    if not request.user.is_verified():
        return False
    verified_at = request.session.get("otp_verified_at")
    return bool(verified_at and (time.time() - verified_at) < OTP_VERIFY_TTL)


class AdminOTPMiddleware:
    """Enforce TOTP two-factor authentication for all admin pages.

    Uses a session timestamp to enforce 24-hour re-verification.
    """

    WHITELISTED_PREFIXES = (
        "/admin/login/",
        "/admin/logout/",
        "/admin/otp/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        if not path.startswith("/admin/"):
            return self.get_response(request)

        if any(path.startswith(prefix) for prefix in self.WHITELISTED_PREFIXES):
            return self.get_response(request)

        if not hasattr(request, "user") or not request.user.is_authenticated:
            return self.get_response(request)

        if not request.user.is_staff:
            return self.get_response(request)

        if is_otp_verified(request):
            return self.get_response(request)

        request.session["admin_otp_next"] = path

        from django_otp.plugins.otp_totp.models import TOTPDevice

        has_device = TOTPDevice.objects.filter(
            user=request.user, confirmed=True
        ).exists()

        if has_device:
            return redirect("admin_otp_verify")
        else:
            return redirect("admin_otp_setup")
