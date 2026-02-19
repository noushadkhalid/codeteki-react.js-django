"""
Engagement Engine - Computes engagement profiles for deals from EmailLog data.

Used by the autopilot system to make smart decisions about email cadence,
detect burnout, classify engagement tiers, and provide AI with context.
"""

from dataclasses import dataclass, field
from django.utils import timezone


ENGAGEMENT_TIER_CHOICES = [
    ('engaged', 'Engaged'),
    ('hot', 'Hot'),
    ('warm', 'Warm'),
    ('lurker', 'Lurker'),
    ('cold', 'Cold'),
    ('ghost', 'Ghost'),
]


@dataclass
class EngagementProfile:
    """Engagement metrics computed from a deal's EmailLog history."""

    # Core counts
    total_sent: int = 0
    total_opened: int = 0
    total_clicked: int = 0
    total_replied: int = 0

    # Rates
    open_rate: float = 0.0
    click_rate: float = 0.0

    # Behavioral signals
    last_open_days_ago: int | None = None
    last_click_days_ago: int | None = None
    last_reply_days_ago: int | None = None
    opens_last_7_days: int = 0
    consecutive_unopened: int = 0

    # Tier
    tier: str = 'cold'

    # Burnout detection
    is_burnout_risk: bool = False

    # Recommendations
    recommended_action: str = 'send_now'
    recommended_wait_days: int = 0


def get_engagement_profile(deal) -> EngagementProfile:
    """
    Compute an engagement profile for a deal from its EmailLog data.

    Args:
        deal: Deal instance (must have related email_logs)

    Returns:
        EngagementProfile with computed metrics
    """
    from crm.models import EmailLog

    now = timezone.now()
    profile = EngagementProfile()

    # Get all sent emails for this deal
    emails = EmailLog.objects.filter(
        deal=deal,
        sent_at__isnull=False,
    ).order_by('-sent_at')

    if not emails.exists():
        profile.tier = 'cold'
        profile.recommended_action = 'send_now'
        return profile

    profile.total_sent = emails.count()
    profile.total_opened = emails.filter(opened=True).count()
    profile.total_clicked = emails.filter(clicked=True).count()
    profile.total_replied = emails.filter(replied=True).count()

    # Rates
    if profile.total_sent > 0:
        profile.open_rate = profile.total_opened / profile.total_sent
        profile.click_rate = profile.total_clicked / profile.total_sent

    # Last open/click/reply days ago
    last_opened = emails.filter(opened=True, opened_at__isnull=False).first()
    if last_opened and last_opened.opened_at:
        profile.last_open_days_ago = (now - last_opened.opened_at).days

    last_clicked = emails.filter(clicked=True, clicked_at__isnull=False).first()
    if last_clicked and last_clicked.clicked_at:
        profile.last_click_days_ago = (now - last_clicked.clicked_at).days

    last_replied = emails.filter(replied=True, replied_at__isnull=False).first()
    if last_replied and last_replied.replied_at:
        profile.last_reply_days_ago = (now - last_replied.replied_at).days

    # Opens in last 7 days
    seven_days_ago = now - timezone.timedelta(days=7)
    profile.opens_last_7_days = emails.filter(
        opened=True,
        opened_at__gte=seven_days_ago,
    ).count()

    # Consecutive unopened (count from most recent backwards)
    consecutive = 0
    for email in emails:
        if not email.opened:
            consecutive += 1
        else:
            break
    profile.consecutive_unopened = consecutive

    # Burnout risk: 3+ consecutive unopened
    profile.is_burnout_risk = profile.consecutive_unopened >= 3

    # Classify tier
    profile.tier = _classify_tier(profile)

    # Determine recommended action
    profile.recommended_action, profile.recommended_wait_days = _get_recommendation(profile)

    return profile


def _classify_tier(profile: EngagementProfile) -> str:
    """
    Classify engagement tier based on profile metrics.

    Tiers (from most to least engaged):
    - engaged: Has replied positively
    - hot: Opened/clicked in last 7 days, open_rate > 50%
    - warm: Opened at least once, last open within 14 days
    - lurker: Opened 1-2 emails ever, but not recently (>14 days)
    - cold: Sent 2+ emails, zero opens
    - ghost: Sent 3+ emails, zero opens, 3+ consecutive unopened
    """
    # Engaged: has replied
    if profile.total_replied > 0:
        return 'engaged'

    # Ghost: 3+ sent, zero opens, 3+ consecutive unopened
    if (profile.total_sent >= 3
            and profile.total_opened == 0
            and profile.consecutive_unopened >= 3):
        return 'ghost'

    # Cold: 2+ sent, zero opens
    if profile.total_sent >= 2 and profile.total_opened == 0:
        return 'cold'

    # Hot: opened/clicked recently, good open rate
    if (profile.opens_last_7_days > 0
            or (profile.last_click_days_ago is not None and profile.last_click_days_ago <= 7)):
        if profile.open_rate > 0.5:
            return 'hot'

    # Warm: opened at least once, last open within 14 days
    if profile.total_opened > 0:
        if profile.last_open_days_ago is not None and profile.last_open_days_ago <= 14:
            return 'warm'

    # Lurker: opened 1-2 emails but not recently
    if 1 <= profile.total_opened <= 2:
        return 'lurker'

    # Default: warm if they've opened anything, cold otherwise
    if profile.total_opened > 0:
        return 'warm'

    return 'cold'


def _get_recommendation(profile: EngagementProfile) -> tuple[str, int]:
    """
    Determine recommended action based on engagement profile.

    Returns:
        (action, wait_days) tuple
        action: 'send_now' | 'wait' | 'change_approach' | 'pause' | 'stop'
    """
    tier = profile.tier

    if tier == 'ghost':
        return 'stop', 0

    if tier == 'engaged':
        return 'send_now', 0

    if tier == 'hot':
        return 'send_now', 0

    if tier == 'warm':
        if profile.is_burnout_risk:
            return 'wait', 7
        return 'send_now', 0

    if tier == 'lurker':
        return 'change_approach', 5

    if tier == 'cold':
        if profile.is_burnout_risk:
            return 'pause', 0
        if profile.total_sent >= 3:
            return 'change_approach', 7
        return 'wait', 5

    return 'send_now', 0


def compute_preferred_send_hour(contact) -> int | None:
    """
    Compute preferred send hour from email open history.

    Requires 3+ opens with timestamps. Returns most common hour (0-23)
    or None if insufficient data.
    """
    from crm.models import EmailLog

    opens = EmailLog.objects.filter(
        to_email=contact.email,
        opened=True,
        opened_at__isnull=False,
    ).values_list('opened_at', flat=True)

    if len(opens) < 3:
        return None

    # Count opens by hour (using local timezone)
    from collections import Counter
    from django.utils.timezone import localtime
    hour_counts = Counter(localtime(dt).hour for dt in opens)
    return hour_counts.most_common(1)[0][0]


def get_engagement_summary_for_ai(deal) -> str:
    """
    Get a formatted engagement summary string for inclusion in AI prompts.

    Args:
        deal: Deal instance

    Returns:
        Multi-line string with engagement data for AI consumption
    """
    profile = get_engagement_profile(deal)

    lines = [
        "ENGAGEMENT PROFILE:",
        f"  Engagement Tier: {profile.tier.upper()}",
        f"  Emails Sent: {profile.total_sent}",
        f"  Open Rate: {profile.open_rate:.0%} ({profile.total_opened}/{profile.total_sent})" if profile.total_sent > 0 else "  Open Rate: N/A (no emails sent)",
        f"  Click Rate: {profile.click_rate:.0%}" if profile.total_sent > 0 else "  Click Rate: N/A",
        f"  Replies: {profile.total_replied}",
        f"  Last Open: {profile.last_open_days_ago} days ago" if profile.last_open_days_ago is not None else "  Last Open: never",
        f"  Last Click: {profile.last_click_days_ago} days ago" if profile.last_click_days_ago is not None else "  Last Click: never",
        f"  Last Reply: {profile.last_reply_days_ago} days ago" if profile.last_reply_days_ago is not None else "  Last Reply: never",
        f"  Opens Last 7 Days: {profile.opens_last_7_days}",
        f"  Consecutive Unopened: {profile.consecutive_unopened}",
        f"  Burnout Risk: {'YES' if profile.is_burnout_risk else 'No'}",
        f"  Recommended Action: {profile.recommended_action}",
    ]

    if profile.recommended_wait_days > 0:
        lines.append(f"  Recommended Wait: {profile.recommended_wait_days} days")

    return "\n".join(lines)
