from django.shortcuts import redirect


class AdminOTPMiddleware:
    """Enforce TOTP two-factor authentication for all admin pages.

    After a user logs in with username/password, this middleware checks
    whether they have completed OTP verification (via django-otp's
    ``is_verified()``).  Unverified users are redirected to the OTP
    setup or verification page.
    """

    # Paths that should never trigger OTP checks (login, logout, and OTP
    # flow pages themselves).
    WHITELISTED_PREFIXES = (
        "/admin/login/",
        "/admin/logout/",
        "/admin/otp/",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Only intercept /admin/ paths — API / frontend are unaffected.
        if not path.startswith("/admin/"):
            return self.get_response(request)

        # Let whitelisted paths through (login, logout, OTP pages).
        if any(path.startswith(prefix) for prefix in self.WHITELISTED_PREFIXES):
            return self.get_response(request)

        # Anonymous users are handled by Django's built-in login_required
        # logic on the admin site — no action needed here.
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return self.get_response(request)

        # Only enforce for staff users who can actually access admin.
        if not request.user.is_staff:
            return self.get_response(request)

        # django-otp's OTPMiddleware adds ``is_verified()`` to the user.
        if request.user.is_verified():
            return self.get_response(request)

        # Save the originally requested URL so we can redirect back after
        # OTP verification.
        request.session["admin_otp_next"] = path

        # Check whether the user has *any* confirmed TOTP device.
        from django_otp.plugins.otp_totp.models import TOTPDevice

        has_device = TOTPDevice.objects.filter(
            user=request.user, confirmed=True
        ).exists()

        if has_device:
            return redirect("admin_otp_verify")
        else:
            return redirect("admin_otp_setup")
