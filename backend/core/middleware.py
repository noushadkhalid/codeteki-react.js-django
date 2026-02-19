import time

from django.shortcuts import redirect

# OTP verification expires after 24 hours (in seconds).
OTP_VERIFY_TTL = 24 * 60 * 60


class AdminOTPMiddleware:
    """Enforce TOTP two-factor authentication for all admin pages.

    After a user logs in with username/password, this middleware checks
    whether they have completed OTP verification (via django-otp's
    ``is_verified()``) AND that the verification happened within the
    last 24 hours.  Expired verifications force a re-verify.
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

        # Check both: django-otp says verified AND our timestamp is fresh.
        if request.user.is_verified():
            verified_at = request.session.get("otp_verified_at")
            if verified_at and (time.time() - verified_at) < OTP_VERIFY_TTL:
                return self.get_response(request)

            # Verification expired — clear OTP state so is_verified() returns
            # False on the next request after we redirect.
            if "_otp_device_id" in request.session:
                del request.session["_otp_device_id"]
            request.session.pop("otp_verified_at", None)

        request.session["admin_otp_next"] = path

        from django_otp.plugins.otp_totp.models import TOTPDevice

        has_device = TOTPDevice.objects.filter(
            user=request.user, confirmed=True
        ).exists()

        if has_device:
            return redirect("admin_otp_verify")
        else:
            return redirect("admin_otp_setup")
