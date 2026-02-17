# Autopilot Engagement System Migration
# - Removes DripCampaign, DripStep, CampaignEnrollment models and EmailLog FK fields
# - Adds engagement_tier, autopilot_paused to Deal
# - Adds subject_variant_b to PipelineStage
# - Adds ab_variant to EmailLog

from django.db import migrations, models
import django.db.models.deletion


def clean_drip_campaign_artifacts(apps, schema_editor):
    """Remove drip campaign tables and columns that may exist from a previously applied migration."""
    with schema_editor.connection.cursor() as cursor:
        # Drop indexes on drip columns first (required before DROP COLUMN in SQLite)
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='crm_emaillog'"
        )
        drip_indexes = [
            row[0] for row in cursor.fetchall()
            if any(kw in row[0] for kw in ['campaign_enrollment', 'drip_step'])
        ]
        for idx in drip_indexes:
            cursor.execute(f'DROP INDEX IF EXISTS "{idx}"')

        # Remove drip FK columns from emaillog using DROP COLUMN (SQLite 3.35+)
        cursor.execute("PRAGMA table_info(crm_emaillog)")
        columns = {row[1] for row in cursor.fetchall()}

        for col in ['campaign_enrollment_id', 'drip_step_id', 'ab_variant']:
            if col in columns:
                cursor.execute(f'ALTER TABLE "crm_emaillog" DROP COLUMN "{col}"')

        # Drop drip tables (order matters for FK constraints)
        for table in ['crm_campaignenrollment', 'crm_dripstep', 'crm_dripcampaign']:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")

        # Clean up old migration record if it exists
        cursor.execute(
            "DELETE FROM django_migrations WHERE app='crm' AND name='0024_drip_campaign_system'"
        )


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0023_update_emaillog_default_from_email'),
    ]

    operations = [
        # Phase 1: Clean up any drip campaign artifacts from previously applied migration
        migrations.RunPython(clean_drip_campaign_artifacts, migrations.RunPython.noop),

        # Phase 2: Add new autopilot fields to Deal
        migrations.AddField(
            model_name='deal',
            name='autopilot_paused',
            field=models.BooleanField(default=False, help_text='Pause autopilot for this deal (manual override)'),
        ),
        migrations.AddField(
            model_name='deal',
            name='engagement_tier',
            field=models.CharField(blank=True, choices=[('', 'Unknown'), ('engaged', 'Engaged'), ('hot', 'Hot'), ('warm', 'Warm'), ('lurker', 'Lurker'), ('cold', 'Cold'), ('ghost', 'Ghost')], default='', help_text='Auto-computed engagement tier from email activity', max_length=20),
        ),

        # Phase 3: Add A/B testing to PipelineStage
        migrations.AddField(
            model_name='pipelinestage',
            name='subject_variant_b',
            field=models.CharField(blank=True, help_text='A/B test subject line. Leave blank to disable.', max_length=255),
        ),

        # Phase 4: Add ab_variant to EmailLog (cleaned above if it existed from old migration)
        migrations.AddField(
            model_name='emaillog',
            name='ab_variant',
            field=models.CharField(blank=True, help_text='A/B test variant: A or B', max_length=1),
        ),

        # Phase 5: Ensure deal FK is nullable on EmailLog
        migrations.AlterField(
            model_name='emaillog',
            name='deal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='email_logs', to='crm.deal'),
        ),
    ]
