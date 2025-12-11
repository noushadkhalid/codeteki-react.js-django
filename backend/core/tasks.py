"""
Celery tasks for background processing of SEO audits.

These tasks run asynchronously to prevent request timeouts when
auditing multiple URLs with Lighthouse.
"""

import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_lighthouse_audit_task(self, audit_id: int) -> dict:
    """
    Run Lighthouse audit for a SiteAudit in the background.

    Args:
        audit_id: ID of the SiteAudit to process

    Returns:
        dict with audit results
    """
    from .models import SiteAudit
    from .services.lighthouse import LighthouseService

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting background Lighthouse audit for {audit.name} (ID: {audit_id})")

        # Update task ID on the audit for tracking
        audit.celery_task_id = self.request.id
        audit.save(update_fields=['celery_task_id'])

        # Run the audit
        service = LighthouseService(audit)

        if not service.check_lighthouse_installed():
            audit.status = SiteAudit.STATUS_FAILED
            audit.save(update_fields=['status'])
            return {
                "success": False,
                "error": "Lighthouse CLI not installed on server"
            }

        result = audit.run_audit()

        logger.info(f"Completed Lighthouse audit for {audit.name}: {result.get('pages_audited', 0)} pages")
        return result

    except SiteAudit.DoesNotExist:
        logger.error(f"SiteAudit with ID {audit_id} not found")
        return {"success": False, "error": f"Audit {audit_id} not found"}

    except Exception as e:
        logger.exception(f"Error in Lighthouse audit task: {e}")

        # Update audit status to failed
        try:
            audit = SiteAudit.objects.get(id=audit_id)
            audit.status = SiteAudit.STATUS_FAILED
            audit.save(update_fields=['status'])
        except:
            pass

        # Retry on transient errors
        raise self.retry(exc=e)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def run_pagespeed_audit_task(self, audit_id: int) -> dict:
    """
    Run PageSpeed analysis for a SiteAudit in the background.

    Args:
        audit_id: ID of the SiteAudit to process

    Returns:
        dict with audit results
    """
    from .models import SiteAudit, PageAudit, AuditIssue
    from .services.pagespeed import PageSpeedService

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting background PageSpeed audit for {audit.name} (ID: {audit_id})")

        # Update task ID and status
        audit.celery_task_id = self.request.id
        audit.status = SiteAudit.STATUS_RUNNING
        audit.started_at = timezone.now()
        audit.save(update_fields=['celery_task_id', 'status', 'started_at'])

        service = PageSpeedService()
        urls = audit.target_urls or [f"https://{audit.domain}/"]

        pages_done = 0
        errors = []

        for url in urls:
            try:
                data = service.analyze_url(url, audit.strategy)
                if not data or not data.get('success'):
                    errors.append({"url": url, "error": "PageSpeed API failed"})
                    continue

                # Save to PageAudit
                page_audit, created = PageAudit.objects.update_or_create(
                    site_audit=audit,
                    url=url,
                    defaults={
                        'strategy': audit.strategy,
                        'performance_score': data.get('lab_performance_score'),
                        'seo_score': data.get('seo_score'),
                        'accessibility_score': data.get('accessibility_score'),
                        'best_practices_score': data.get('best_practices_score'),
                        'lcp': data.get('lab_lcp'),
                        'cls': data.get('lab_cls'),
                        'fcp': data.get('lab_fcp'),
                        'tbt': data.get('lab_tbt'),
                        'si': data.get('lab_si'),
                        'ttfb': data.get('field_ttfb'),
                        'status': 'completed',
                        'raw_data': data.get('raw_data', {})
                    }
                )

                # Create issues from opportunities and diagnostics
                if created:
                    for category in ['opportunities', 'diagnostics']:
                        for item in data.get(category, []):
                            AuditIssue.objects.create(
                                page_audit=page_audit,
                                audit_id=item.get('id', ''),
                                title=item.get('title', ''),
                                description=item.get('description', ''),
                                category='performance',
                                severity='warning' if item.get('score', 1) < 0.9 else 'info',
                                score=item.get('score'),
                                display_value=item.get('displayValue', ''),
                                savings_ms=item.get('numericValue', 0) if 'ms' in item.get('displayValue', '') else 0,
                                details=item.get('details', {}),
                            )

                pages_done += 1
                logger.info(f"Completed PageSpeed for {url} ({pages_done}/{len(urls)})")

            except Exception as e:
                logger.error(f"Error analyzing {url}: {e}")
                errors.append({"url": url, "error": str(e)})

        # Update audit with results
        page_audits = audit.page_audits.all()
        if page_audits.exists():
            from django.db.models import Avg
            averages = page_audits.aggregate(
                avg_perf=Avg('performance_score'),
                avg_seo=Avg('seo_score'),
                avg_acc=Avg('accessibility_score'),
                avg_bp=Avg('best_practices_score'),
            )
            audit.avg_performance = averages['avg_perf']
            audit.avg_seo = averages['avg_seo']
            audit.avg_accessibility = averages['avg_acc']
            audit.avg_best_practices = averages['avg_bp']

        audit.status = SiteAudit.STATUS_COMPLETED
        audit.completed_at = timezone.now()
        audit.total_pages = pages_done
        audit.total_issues = AuditIssue.objects.filter(page_audit__site_audit=audit).count()
        audit.save()

        logger.info(f"Completed PageSpeed audit for {audit.name}: {pages_done} pages")

        return {
            "success": True,
            "pages_audited": pages_done,
            "total_issues": audit.total_issues,
            "errors": errors
        }

    except SiteAudit.DoesNotExist:
        logger.error(f"SiteAudit with ID {audit_id} not found")
        return {"success": False, "error": f"Audit {audit_id} not found"}

    except Exception as e:
        logger.exception(f"Error in PageSpeed audit task: {e}")

        try:
            audit = SiteAudit.objects.get(id=audit_id)
            audit.status = SiteAudit.STATUS_FAILED
            audit.save(update_fields=['status'])
        except:
            pass

        raise self.retry(exc=e)


@shared_task(bind=True)
def generate_ai_analysis_task(self, audit_id: int) -> dict:
    """
    Generate AI analysis for completed audit in the background.

    Args:
        audit_id: ID of the SiteAudit to analyze

    Returns:
        dict with analysis status
    """
    from .models import SiteAudit
    from .services.seo_ai import SEOAuditAIEngine

    try:
        audit = SiteAudit.objects.get(id=audit_id)
        logger.info(f"Starting AI analysis for {audit.name}")

        engine = SEOAuditAIEngine(audit)
        analysis = engine.generate_analysis()

        if analysis:
            audit.ai_analysis = analysis
            audit.save(update_fields=['ai_analysis'])
            logger.info(f"Completed AI analysis for {audit.name}")
            return {"success": True}
        else:
            return {"success": False, "error": "Failed to generate analysis"}

    except SiteAudit.DoesNotExist:
        return {"success": False, "error": f"Audit {audit_id} not found"}
    except Exception as e:
        logger.exception(f"Error generating AI analysis: {e}")
        return {"success": False, "error": str(e)}
