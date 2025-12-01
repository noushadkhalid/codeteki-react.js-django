"""
PageSpeed Insights API Service.

This service uses Google's PageSpeed Insights API to get:
- Lab data (Lighthouse results)
- Field data (Real User Metrics from Chrome User Experience Report)
- Origin-level metrics (site-wide performance)

Benefits over Lighthouse CLI:
- Real user data (CrUX) - actual visitor experience
- No server-side Chrome required
- Origin-level metrics for overall site health

Limitations:
- ~400 queries/day free tier
- Public URLs only (no localhost/staging)
"""

from __future__ import annotations

import requests
import logging
from typing import Optional

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class PageSpeedService:
    """
    Service for running PageSpeed Insights analysis.

    Uses Google PageSpeed Insights API v5.
    """

    API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self):
        """Initialize PageSpeed service."""
        self.api_key = getattr(settings, "GOOGLE_API_KEY", "")

    @property
    def enabled(self) -> bool:
        """Check if service is configured."""
        return bool(self.api_key)

    def analyze_url(self, url: str, strategy: str = "mobile") -> dict:
        """
        Analyze a URL using PageSpeed Insights API.

        Args:
            url: URL to analyze
            strategy: "mobile" or "desktop"

        Returns:
            dict with analysis results
        """
        from ..models import PageSpeedResult

        result = {
            "success": False,
            "url": url,
            "strategy": strategy,
        }

        if not self.enabled:
            result["error"] = "PageSpeed API not configured. Set GOOGLE_API_KEY in settings."
            return result

        try:
            # Build request
            params = {
                "url": url,
                "key": self.api_key,
                "strategy": strategy,
                "category": ["performance", "accessibility", "best-practices", "seo"],
            }

            logger.info(f"Running PageSpeed analysis for {url}")
            response = requests.get(self.API_URL, params=params, timeout=60)

            if response.status_code != 200:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get("error", {}).get("message", response.text[:200])
                result["error"] = f"API error ({response.status_code}): {error_msg}"
                return result

            data = response.json()

            # Extract lab data (Lighthouse)
            lighthouse = data.get("lighthouseResult", {})
            categories = lighthouse.get("categories", {})
            audits = lighthouse.get("audits", {})

            result["lab_performance_score"] = self._extract_score(categories.get("performance"))

            # Extract lab metrics
            result["lab_lcp"] = self._extract_metric(audits, "largest-contentful-paint", ms_to_s=True)
            result["lab_fcp"] = self._extract_metric(audits, "first-contentful-paint", ms_to_s=True)
            result["lab_cls"] = self._extract_metric(audits, "cumulative-layout-shift")
            result["lab_tbt"] = self._extract_metric(audits, "total-blocking-time")
            result["lab_si"] = self._extract_metric(audits, "speed-index", ms_to_s=True)

            # Extract field data (CrUX)
            loading_exp = data.get("loadingExperience", {})
            origin_loading = data.get("originLoadingExperience", {})

            if loading_exp.get("metrics"):
                result["has_field_data"] = True
                field_metrics = loading_exp.get("metrics", {})
                result["field_lcp"] = self._extract_crux_metric(field_metrics, "LARGEST_CONTENTFUL_PAINT_MS", ms_to_s=True)
                result["field_fid"] = self._extract_crux_metric(field_metrics, "FIRST_INPUT_DELAY_MS")
                result["field_inp"] = self._extract_crux_metric(field_metrics, "INTERACTION_TO_NEXT_PAINT")
                result["field_cls"] = self._extract_crux_metric(field_metrics, "CUMULATIVE_LAYOUT_SHIFT_SCORE")
                result["field_fcp"] = self._extract_crux_metric(field_metrics, "FIRST_CONTENTFUL_PAINT_MS", ms_to_s=True)
                result["field_ttfb"] = self._extract_crux_metric(field_metrics, "EXPERIMENTAL_TIME_TO_FIRST_BYTE")
                result["overall_category"] = loading_exp.get("overall_category", "")
            else:
                result["has_field_data"] = False
                result["overall_category"] = "NO_DATA"

            # Extract origin-level metrics
            if origin_loading.get("metrics"):
                origin_metrics = origin_loading.get("metrics", {})
                result["origin_lcp"] = self._extract_crux_metric(origin_metrics, "LARGEST_CONTENTFUL_PAINT_MS", ms_to_s=True)
                result["origin_inp"] = self._extract_crux_metric(origin_metrics, "INTERACTION_TO_NEXT_PAINT")
                result["origin_cls"] = self._extract_crux_metric(origin_metrics, "CUMULATIVE_LAYOUT_SHIFT_SCORE")

            # Extract issues from Lighthouse data embedded in PageSpeed response
            result["issues"] = self._extract_issues(lighthouse)

            # Store raw data (trimmed but with audit details)
            result["raw_data"] = self._trim_raw_data(data)

            result["success"] = True

        except requests.Timeout:
            result["error"] = "PageSpeed API request timed out"
        except requests.RequestException as e:
            result["error"] = f"Network error: {str(e)}"
        except Exception as e:
            result["error"] = str(e)
            logger.exception(f"Error analyzing {url}")

        return result

    def analyze_and_save(self, url: str, strategy: str = "mobile", page_audit=None) -> Optional["PageSpeedResult"]:
        """
        Analyze URL and save results to database.

        Args:
            url: URL to analyze
            strategy: "mobile" or "desktop"
            page_audit: Optional PageAudit to link results to

        Returns:
            PageSpeedResult instance or None on error
        """
        from ..models import PageSpeedResult, AuditIssue

        analysis = self.analyze_url(url, strategy)

        if not analysis.get("success"):
            logger.error(f"PageSpeed analysis failed: {analysis.get('error')}")
            return None

        # Create PageSpeedResult
        result = PageSpeedResult.objects.create(
            page_audit=page_audit,
            url=url,
            strategy=strategy,
            lab_performance_score=analysis.get("lab_performance_score"),
            lab_lcp=analysis.get("lab_lcp"),
            lab_fcp=analysis.get("lab_fcp"),
            lab_cls=analysis.get("lab_cls"),
            lab_tbt=analysis.get("lab_tbt"),
            lab_si=analysis.get("lab_si"),
            field_lcp=analysis.get("field_lcp"),
            field_fid=analysis.get("field_fid"),
            field_inp=analysis.get("field_inp"),
            field_cls=analysis.get("field_cls"),
            field_fcp=analysis.get("field_fcp"),
            field_ttfb=analysis.get("field_ttfb"),
            origin_lcp=analysis.get("origin_lcp"),
            origin_inp=analysis.get("origin_inp"),
            origin_cls=analysis.get("origin_cls"),
            overall_category=analysis.get("overall_category", ""),
            raw_data=analysis.get("raw_data", {}),
        )

        # Save issues if page_audit is provided
        if page_audit and analysis.get("issues"):
            for issue_data in analysis["issues"]:
                AuditIssue.objects.create(
                    page_audit=page_audit,
                    audit_id=issue_data.get("id", ""),
                    title=issue_data.get("title", ""),
                    description=issue_data.get("description", ""),
                    category=issue_data.get("category", ""),
                    severity=issue_data.get("severity", "info"),
                    score=issue_data.get("score"),
                    display_value=issue_data.get("display_value", ""),
                    savings_ms=issue_data.get("savings_ms", 0),
                    savings_bytes=issue_data.get("savings_bytes", 0),
                    details=issue_data.get("details", {}),
                )

        return result

    def compare_lab_vs_field(self, url: str, strategy: str = "mobile") -> dict:
        """
        Compare lab data (Lighthouse) vs field data (CrUX).

        Useful for identifying discrepancies between synthetic and real-world performance.

        Args:
            url: URL to analyze
            strategy: "mobile" or "desktop"

        Returns:
            dict with comparison data
        """
        analysis = self.analyze_url(url, strategy)

        if not analysis.get("success"):
            return {"success": False, "error": analysis.get("error")}

        comparison = {
            "success": True,
            "url": url,
            "strategy": strategy,
            "has_field_data": analysis.get("has_field_data", False),
            "metrics": {},
        }

        # Compare metrics that exist in both
        metrics_to_compare = [
            ("lcp", "Largest Contentful Paint"),
            ("fcp", "First Contentful Paint"),
            ("cls", "Cumulative Layout Shift"),
        ]

        for metric_key, metric_name in metrics_to_compare:
            lab_value = analysis.get(f"lab_{metric_key}")
            field_value = analysis.get(f"field_{metric_key}")

            comparison["metrics"][metric_key] = {
                "name": metric_name,
                "lab": lab_value,
                "field": field_value,
                "difference": None,
                "assessment": None,
            }

            if lab_value is not None and field_value is not None:
                diff = field_value - lab_value
                comparison["metrics"][metric_key]["difference"] = diff

                # Assess the difference
                if abs(diff) < 0.1 * lab_value:
                    assessment = "consistent"
                elif field_value > lab_value:
                    assessment = "real_users_slower"
                else:
                    assessment = "real_users_faster"

                comparison["metrics"][metric_key]["assessment"] = assessment

        return comparison

    def _extract_score(self, category_data: Optional[dict]) -> Optional[int]:
        """Extract score from category data (0-100)."""
        if not category_data:
            return None
        score = category_data.get("score")
        if score is not None:
            return int(score * 100)
        return None

    def _extract_metric(self, audits: dict, audit_id: str, ms_to_s: bool = False) -> Optional[float]:
        """Extract metric value from audits."""
        audit = audits.get(audit_id, {})
        value = audit.get("numericValue")
        if value is not None and ms_to_s:
            return value / 1000
        return value

    def _extract_crux_metric(self, metrics: dict, metric_id: str, ms_to_s: bool = False) -> Optional[float]:
        """Extract metric from CrUX data (75th percentile)."""
        metric = metrics.get(metric_id, {})
        percentile = metric.get("percentile")
        if percentile is not None:
            if ms_to_s:
                return percentile / 1000
            return percentile
        return None

    def _extract_issues(self, lighthouse_data: dict) -> list:
        """Extract issues/opportunities from Lighthouse data in PageSpeed response."""
        issues = []
        audits = lighthouse_data.get("audits", {})
        categories = lighthouse_data.get("categories", {})

        # Map audit IDs to categories
        audit_to_category = {}
        for cat_id, cat_data in categories.items():
            for audit_ref in cat_data.get("auditRefs", []):
                audit_to_category[audit_ref.get("id")] = cat_id

        for audit_id, audit_data in audits.items():
            # Skip passed/informational audits
            score = audit_data.get("score")
            if score is None or score == 1:
                continue

            # Determine severity
            if score == 0:
                severity = "error"
            elif score < 0.5:
                severity = "warning"
            else:
                severity = "info"

            # Get category
            category = audit_to_category.get(audit_id, "performance")

            # Extract savings
            savings_ms = 0
            savings_bytes = 0
            details = audit_data.get("details", {})
            if details.get("overallSavingsMs"):
                savings_ms = details["overallSavingsMs"]
            if details.get("overallSavingsBytes"):
                savings_bytes = details["overallSavingsBytes"]

            issues.append({
                "id": audit_id,
                "title": audit_data.get("title", ""),
                "description": audit_data.get("description", ""),
                "category": category,
                "severity": severity,
                "score": score,
                "display_value": audit_data.get("displayValue", ""),
                "savings_ms": savings_ms,
                "savings_bytes": savings_bytes,
                "details": self._trim_details(details),
            })

        # Sort by severity and savings
        severity_order = {"error": 0, "warning": 1, "info": 2}
        issues.sort(key=lambda x: (severity_order.get(x["severity"], 3), -x["savings_ms"]))

        return issues

    def _trim_details(self, details: dict) -> dict:
        """Trim details while preserving important diagnostic data."""
        if not details:
            return {}

        trimmed = {"type": details.get("type")}

        # Keep headings and summary
        if "headings" in details:
            trimmed["headings"] = details["headings"]
        if "summary" in details:
            trimmed["summary"] = details["summary"]
        if "overallSavingsMs" in details:
            trimmed["overallSavingsMs"] = details["overallSavingsMs"]
        if "overallSavingsBytes" in details:
            trimmed["overallSavingsBytes"] = details["overallSavingsBytes"]

        # Keep items with important fields
        if "items" in details:
            trimmed_items = []
            for item in details["items"][:15]:
                trimmed_item = {}
                # Keep all important fields
                for key in ["url", "totalBytes", "wastedBytes", "wastedMs", "cacheLifetimeMs",
                           "cacheHitProbability", "score", "transferSize", "resourceSize"]:
                    if key in item:
                        trimmed_item[key] = item[key]
                # Handle node (DOM element) data
                if "node" in item:
                    node = item["node"]
                    trimmed_item["node"] = {
                        "selector": node.get("selector", "")[:300],
                        "snippet": node.get("snippet", "")[:500],
                        "nodeLabel": node.get("nodeLabel", "")[:200],
                    }
                if trimmed_item:
                    trimmed_items.append(trimmed_item)
            trimmed["items"] = trimmed_items
            trimmed["total_items"] = len(details["items"])

        return trimmed

    def _trim_raw_data(self, data: dict) -> dict:
        """Trim raw API response while keeping useful diagnostic data."""
        lighthouse = data.get("lighthouseResult", {})

        return {
            "id": data.get("id"),
            "analysisUTCTimestamp": data.get("analysisUTCTimestamp"),
            "loadingExperience": {
                "id": data.get("loadingExperience", {}).get("id"),
                "overall_category": data.get("loadingExperience", {}).get("overall_category"),
                "metrics": data.get("loadingExperience", {}).get("metrics", {}),
            },
            "originLoadingExperience": {
                "id": data.get("originLoadingExperience", {}).get("id"),
                "overall_category": data.get("originLoadingExperience", {}).get("overall_category"),
            },
            "lighthouseResult": {
                "lighthouseVersion": lighthouse.get("lighthouseVersion"),
                "fetchTime": lighthouse.get("fetchTime"),
                "requestedUrl": lighthouse.get("requestedUrl"),
                "finalUrl": lighthouse.get("finalUrl"),
                "runWarnings": lighthouse.get("runWarnings", []),
            },
        }


def quick_pagespeed_check(url: str, strategy: str = "mobile") -> dict:
    """
    Convenience function for quick PageSpeed analysis.

    Args:
        url: URL to analyze
        strategy: "mobile" or "desktop"

    Returns:
        dict with analysis results
    """
    service = PageSpeedService()
    return service.analyze_url(url, strategy)
