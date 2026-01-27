# Generated migration for adding nudge email types

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0018_add_send_to_pipeline_contacts'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emaildraft',
            name='email_type',
            field=models.CharField(
                max_length=50,
                choices=[
                    # Desi Firms - Business Listings
                    ('directory_invitation', 'Directory Invitation'),
                    ('listing_benefits', 'Free Listing Benefits'),
                    ('invitation_followup', 'Invitation Follow-up'),
                    ('onboarding_help', 'Onboarding Help'),
                    # Desi Firms - Events
                    ('event_invitation', 'Event Organizer Invitation'),
                    ('event_benefits', 'Event Platform Benefits'),
                    # Desi Firms - Real Estate
                    ('agent_invitation', 'Agent/Agency Invitation'),
                    ('free_listing', 'Free Property Listing'),
                    # Desi Firms - Classifieds
                    ('classifieds_invitation', 'Classifieds Invitation'),
                    # Desi Firms - Nudge (Registered but inactive users)
                    ('business_nudge', '🔔 Nudge: List Your Business'),
                    ('business_nudge_2', '🔔 Nudge 2: Business Reminder'),
                    ('realestate_nudge', '🔔 Nudge: Become an Agent'),
                    ('realestate_nudge_2', '🔔 Nudge 2: Agent Reminder'),
                    ('events_nudge', '🔔 Nudge: Post Your Events'),
                    ('events_nudge_2', '🔔 Nudge 2: Events Reminder'),
                    # Codeteki - Sales
                    ('services_intro', 'Web/AI Services Introduction'),
                    ('seo_services', 'SEO Services Pitch'),
                    ('sales_followup', 'Sales Follow-up'),
                    ('proposal_followup', 'Proposal Follow-up'),
                    # Codeteki - Backlink
                    ('backlink_pitch', 'Backlink Pitch'),
                    ('guest_post', 'Guest Post Offer'),
                    ('backlink_followup', 'Backlink Follow-up'),
                    # Codeteki - Partnership
                    ('partnership_intro', 'Partnership Introduction'),
                    ('collaboration', 'Collaboration Proposal'),
                    ('partnership_followup', 'Partnership Follow-up'),
                    # Re-engagement / Existing Customers
                    ('existing_customer_update', 'Existing Customer Update'),
                    ('win_back', 'Win-back Email'),
                    ('feature_announcement', 'New Feature Announcement'),
                    ('pricing_update', 'Pricing Update'),
                    # Generic
                    ('invitation', 'General Invitation'),
                    ('followup', 'General Follow-up'),
                    ('custom', 'Custom'),
                ],
                default='invitation',
            ),
        ),
    ]
