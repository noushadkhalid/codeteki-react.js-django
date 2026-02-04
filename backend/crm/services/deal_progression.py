"""
Deal Progression Service

Automatically progress deals through pipeline stages when users take actions.
Call these functions from your real estate app when events occur.
"""

import logging
from django.utils import timezone
from crm.models import Deal, Pipeline, PipelineStage, DealActivity

logger = logging.getLogger(__name__)


def progress_agent_deal(email: str, action: str) -> bool:
    """
    Progress an agent's deal based on their action.

    Args:
        email: Agent's email address
        action: Action taken - 'profile_complete', 'agency_created',
                'team_invited', 'first_listing', 'active_lister'

    Returns:
        True if deal was progressed, False otherwise

    Usage:
        from crm.services.deal_progression import progress_agent_deal

        # When agent completes profile
        progress_agent_deal('agent@example.com', 'profile_complete')

        # When agent creates agency
        progress_agent_deal('agent@example.com', 'agency_created')

        # When agent adds first listing
        progress_agent_deal('agent@example.com', 'first_listing')
    """

    # Map actions to target stage names
    action_to_stage = {
        'profile_complete': 'Profile Complete',
        'agency_created': 'Agency Created',
        'team_invited': 'Team Invited',
        'first_listing': 'First Listing',
        'active_lister': 'Active Lister',
    }

    target_stage_name = action_to_stage.get(action)
    if not target_stage_name:
        logger.warning(f"Unknown action: {action}")
        return False

    try:
        # Find the Agents & Agencies pipeline
        pipeline = Pipeline.objects.filter(
            name__icontains='Agents',
            is_active=True
        ).first()

        if not pipeline:
            logger.warning("Agents & Agencies pipeline not found")
            return False

        # Find active deal for this contact in this pipeline
        deal = Deal.objects.filter(
            contact__email__iexact=email,
            pipeline=pipeline,
            status='active'
        ).first()

        if not deal:
            logger.info(f"No active deal found for {email} in {pipeline.name}")
            return False

        # Find target stage
        target_stage = pipeline.stages.filter(name__iexact=target_stage_name).first()
        if not target_stage:
            logger.warning(f"Stage '{target_stage_name}' not found in {pipeline.name}")
            return False

        # Check if already at or past this stage
        if deal.current_stage and deal.current_stage.order >= target_stage.order:
            logger.info(f"Deal already at or past {target_stage_name}")
            return False

        # Move to target stage
        old_stage = deal.current_stage.name if deal.current_stage else 'Unknown'
        deal.current_stage = target_stage
        deal.stage_entered_at = timezone.now()

        # If terminal stage, mark as won
        if target_stage.is_terminal:
            deal.status = 'won'
            deal.next_action_date = None
        else:
            # Set next action date based on stage settings
            if target_stage.days_until_followup:
                deal.next_action_date = timezone.now() + timezone.timedelta(
                    days=target_stage.days_until_followup
                )

        deal.save()

        # Log activity
        DealActivity.objects.create(
            deal=deal,
            activity_type='stage_change',
            description=f"Auto-progressed: {old_stage} → {target_stage_name} (action: {action})"
        )

        logger.info(f"Progressed {email} to {target_stage_name}")
        return True

    except Exception as e:
        logger.error(f"Error progressing deal for {email}: {e}")
        return False


def mark_agent_complete(email: str, reason: str = "Completed onboarding") -> bool:
    """
    Mark an agent's deal as complete/won to stop all automation.

    Args:
        email: Agent's email address
        reason: Reason for completion

    Returns:
        True if deal was marked complete, False otherwise

    Usage:
        from crm.services.deal_progression import mark_agent_complete

        # When agent is fully onboarded
        mark_agent_complete('agent@example.com', 'Added 5+ listings')
    """

    try:
        # Find active deals for this contact
        deals = Deal.objects.filter(
            contact__email__iexact=email,
            status='active'
        )

        if not deals.exists():
            logger.info(f"No active deals found for {email}")
            return False

        for deal in deals:
            # Find terminal/final stage in this pipeline
            final_stage = deal.pipeline.stages.filter(is_terminal=True).first()
            if not final_stage:
                final_stage = deal.pipeline.stages.order_by('-order').first()

            old_stage = deal.current_stage.name if deal.current_stage else 'Unknown'

            deal.status = 'won'
            deal.current_stage = final_stage
            deal.next_action_date = None
            deal.save()

            DealActivity.objects.create(
                deal=deal,
                activity_type='status_change',
                description=f"Marked complete: {reason} (was at {old_stage})"
            )

            logger.info(f"Marked {email} as complete in {deal.pipeline.name}")

        return True

    except Exception as e:
        logger.error(f"Error marking deal complete for {email}: {e}")
        return False
