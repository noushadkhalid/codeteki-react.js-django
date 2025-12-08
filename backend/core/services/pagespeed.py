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
            result["seo_score"] = self._extract_score(categories.get("seo"))
            result["accessibility_score"] = self._extract_score(categories.get("accessibility"))
            result["best_practices_score"] = self._extract_score(categories.get("best-practices"))

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
                "details": self._extract_detailed_audit_data(audit_id, audit_data),
            })

        # Sort by severity and savings
        severity_order = {"error": 0, "warning": 1, "info": 2}
        issues.sort(key=lambda x: (severity_order.get(x["severity"], 3), -x["savings_ms"]))

        return issues

    def _extract_detailed_audit_data(self, audit_id: str, audit_data: dict) -> dict:
        """Extract comprehensive detailed data based on specific audit types."""
        details = audit_data.get("details", {})
        if not details:
            return {}

        # Special handling for specific audit types
        handlers = {
            "layout-shift-elements": self._extract_layout_shift_details,
            "uses-http2": self._extract_http_protocol_details,
            "forced-style-recalc": self._extract_forced_reflow_details,
            "errors-in-console": self._extract_console_errors,
            "mainthread-work-breakdown": self._extract_mainthread_breakdown,
            "uses-rel-preconnect": self._extract_preconnect_details,
            "experimental-interaction-to-next-paint": self._extract_inp_details,
            "critical-request-chains": self._extract_critical_chains,
            "render-blocking-resources": self._extract_render_blocking,
            "uses-long-cache-ttl": self._extract_cache_details,
            "unused-javascript": self._extract_unused_js_details,
            "unused-css-rules": self._extract_unused_css_details,
            "long-tasks": self._extract_long_tasks,
            "non-composited-animations": self._extract_animation_issues,
            "dom-size": self._extract_dom_size,
            "bootup-time": self._extract_bootup_time,
            "duplicated-javascript": self._extract_duplicated_js,
            "lcp-lazy-loaded": self._extract_lcp_details,
            "largest-contentful-paint-element": self._extract_lcp_element,
            "color-contrast": self._extract_contrast_issues,
            "button-name": self._extract_element_issues,
            "link-name": self._extract_element_issues,
            "image-alt": self._extract_element_issues,
            "tap-targets": self._extract_tap_target_issues,
        }

        handler = handlers.get(audit_id, self._trim_details)
        return handler(details)

    def _extract_layout_shift_details(self, details: dict) -> dict:
        """Extract detailed layout shift culprits with exact elements and scores."""
        result = {"type": "layout-shift", "elements": []}

        for item in details.get("items", [])[:20]:
            element = {
                "score": item.get("score"),
                "contribution": item.get("contribution"),
            }

            if "node" in item:
                node = item["node"]
                element["selector"] = node.get("selector", "")
                element["snippet"] = node.get("snippet", "")[:500]
                element["nodeLabel"] = node.get("nodeLabel", "")
                if node.get("boundingRect"):
                    element["boundingRect"] = node["boundingRect"]

            # Check for unsized elements (major CLS cause)
            if item.get("cause"):
                element["cause"] = item["cause"]

            result["elements"].append(element)

        result["total_shift"] = sum(e.get("score", 0) for e in result["elements"])
        return result

    def _extract_http_protocol_details(self, details: dict) -> dict:
        """Extract HTTP protocol information for each request."""
        result = {"type": "http-protocol", "requests": []}

        for item in details.get("items", [])[:30]:
            request = {
                "url": item.get("url", ""),
                "protocol": item.get("protocol", ""),
            }
            result["requests"].append(request)

        # Count protocols
        protocols = {}
        for req in result["requests"]:
            proto = req.get("protocol", "unknown")
            protocols[proto] = protocols.get(proto, 0) + 1
        result["protocol_summary"] = protocols

        return result

    def _extract_forced_reflow_details(self, details: dict) -> dict:
        """Extract forced reflow/style recalculation data."""
        result = {"type": "forced-reflow", "sources": []}

        for item in details.get("items", [])[:15]:
            source = {
                "totalTime": item.get("duration") or item.get("totalTime"),
            }

            if "source" in item:
                src = item["source"]
                if isinstance(src, dict):
                    source["url"] = src.get("url", "")
                    source["line"] = src.get("line")
                    source["column"] = src.get("column")
                    source["function"] = src.get("functionName", "")
                else:
                    source["location"] = str(src)

            result["sources"].append(source)

        result["total_reflow_time"] = sum(s.get("totalTime", 0) for s in result["sources"])
        return result

    def _extract_console_errors(self, details: dict) -> dict:
        """Extract browser console errors logged during audit."""
        result = {"type": "console-errors", "errors": []}

        for item in details.get("items", [])[:20]:
            error = {
                "source": item.get("source", ""),
                "description": item.get("description", ""),
                "level": item.get("sourceLocation", {}).get("type", "error"),
            }

            if "sourceLocation" in item:
                loc = item["sourceLocation"]
                error["url"] = loc.get("url", "")
                error["line"] = loc.get("line")
                error["column"] = loc.get("column")

            result["errors"].append(error)

        return result

    def _extract_mainthread_breakdown(self, details: dict) -> dict:
        """Extract main thread work breakdown by category."""
        result = {"type": "mainthread-breakdown", "categories": {}}

        for item in details.get("items", []):
            group = item.get("groupLabel") or item.get("group", "Other")
            duration = item.get("duration", 0)
            result["categories"][group] = duration

        result["total_time"] = sum(result["categories"].values())
        return result

    def _extract_preconnect_details(self, details: dict) -> dict:
        """Extract preconnect hints analysis."""
        result = {"type": "preconnect", "origins": [], "unused": [], "candidates": []}

        for item in details.get("items", [])[:15]:
            origin = {
                "url": item.get("url", ""),
                "wastedMs": item.get("wastedMs", 0),
            }

            # Check if unused preconnect
            if item.get("wastedMs", 0) == 0 and "unused" in str(item).lower():
                result["unused"].append(origin)
            else:
                result["origins"].append(origin)

        return result

    def _extract_inp_details(self, details: dict) -> dict:
        """Extract INP (Interaction to Next Paint) breakdown."""
        result = {"type": "inp-breakdown", "interactions": []}

        for item in details.get("items", [])[:10]:
            interaction = {
                "inputDelay": item.get("inputDelay"),
                "processingDuration": item.get("processingDuration"),
                "presentationDelay": item.get("presentationDelay"),
                "totalDuration": item.get("duration"),
            }

            if "node" in item:
                node = item["node"]
                interaction["element"] = {
                    "selector": node.get("selector", ""),
                    "snippet": node.get("snippet", "")[:300],
                    "nodeLabel": node.get("nodeLabel", ""),
                }

            result["interactions"].append(interaction)

        return result

    def _extract_critical_chains(self, details: dict) -> dict:
        """Extract critical request chain (network dependency tree)."""
        result = {"type": "critical-chains", "longestChain": {}}

        if "longestChain" in details:
            chain = details["longestChain"]
            result["longestChain"] = {
                "length": chain.get("length"),
                "duration": chain.get("duration"),
                "transferSize": chain.get("transferSize"),
            }

        # Extract the actual chains if available
        if "chains" in details:
            result["chains"] = self._flatten_chains(details["chains"])

        return result

    def _flatten_chains(self, chains: dict, depth: int = 0) -> list:
        """Flatten nested chain structure."""
        result = []
        for chain_id, chain in chains.items():
            item = {
                "depth": depth,
                "url": chain.get("request", {}).get("url", ""),
                "startTime": chain.get("request", {}).get("startTime"),
                "endTime": chain.get("request", {}).get("endTime"),
                "transferSize": chain.get("request", {}).get("transferSize"),
            }
            result.append(item)

            if "children" in chain:
                result.extend(self._flatten_chains(chain["children"], depth + 1))

        return result[:20]  # Limit depth

    def _extract_render_blocking(self, details: dict) -> dict:
        """Extract render-blocking resources details."""
        result = {"type": "render-blocking", "resources": []}

        for item in details.get("items", [])[:15]:
            resource = {
                "url": item.get("url", ""),
                "totalBytes": item.get("totalBytes"),
                "wastedMs": item.get("wastedMs", 0),
            }
            result["resources"].append(resource)

        result["total_blocking_time"] = details.get("overallSavingsMs", 0)
        return result

    def _extract_cache_details(self, details: dict) -> dict:
        """Extract cache lifetime details for each resource."""
        result = {"type": "cache-lifetime", "resources": []}

        for item in details.get("items", [])[:25]:
            resource = {
                "url": item.get("url", ""),
                "cacheLifetimeMs": item.get("cacheLifetimeMs"),
                "cacheTTL": self._format_cache_ttl(item.get("cacheLifetimeMs")),
                "totalBytes": item.get("totalBytes"),
                "wastedBytes": item.get("wastedBytes", 0),
                "cacheHitProbability": item.get("cacheHitProbability"),
            }
            result["resources"].append(resource)

        result["total_cacheable_bytes"] = sum(r.get("totalBytes", 0) for r in result["resources"])
        return result

    def _format_cache_ttl(self, ms: int) -> str:
        """Format cache TTL in human-readable format."""
        if ms is None or ms == 0:
            return "None"

        seconds = ms / 1000
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            return f"{int(seconds/60)}m"
        elif seconds < 86400:
            return f"{int(seconds/3600)}h"
        else:
            return f"{int(seconds/86400)}d"

    def _extract_unused_js_details(self, details: dict) -> dict:
        """Extract detailed unused JavaScript breakdown by module."""
        result = {"type": "unused-javascript", "scripts": [], "modules": []}

        for item in details.get("items", [])[:20]:
            script = {
                "url": item.get("url", ""),
                "totalBytes": item.get("totalBytes"),
                "wastedBytes": item.get("wastedBytes", 0),
                "wastedPercent": item.get("wastedPercent"),
            }

            # Extract module-level breakdown from subItems
            if "subItems" in item and item["subItems"].get("items"):
                script["modules"] = []
                for sub in item["subItems"]["items"][:10]:
                    module = {
                        "source": sub.get("source", ""),
                        "sourceBytes": sub.get("sourceBytes"),
                        "sourceWastedBytes": sub.get("sourceWastedBytes", 0),
                    }
                    script["modules"].append(module)
                    result["modules"].append(module)

            result["scripts"].append(script)

        result["total_wasted_bytes"] = details.get("overallSavingsBytes", 0)
        result["total_wasted_ms"] = details.get("overallSavingsMs", 0)
        return result

    def _extract_unused_css_details(self, details: dict) -> dict:
        """Extract detailed unused CSS breakdown."""
        result = {"type": "unused-css", "stylesheets": []}

        for item in details.get("items", [])[:15]:
            stylesheet = {
                "url": item.get("url", ""),
                "totalBytes": item.get("totalBytes"),
                "wastedBytes": item.get("wastedBytes", 0),
                "wastedPercent": item.get("wastedPercent"),
            }
            result["stylesheets"].append(stylesheet)

        result["total_wasted_bytes"] = details.get("overallSavingsBytes", 0)
        return result

    def _extract_long_tasks(self, details: dict) -> dict:
        """Extract long main-thread tasks."""
        result = {"type": "long-tasks", "tasks": []}

        for item in details.get("items", [])[:15]:
            task = {
                "url": item.get("url", ""),
                "startTime": item.get("startTime"),
                "duration": item.get("duration"),
            }
            result["tasks"].append(task)

        result["count"] = len(result["tasks"])
        return result

    def _extract_animation_issues(self, details: dict) -> dict:
        """Extract non-composited animation issues."""
        result = {"type": "animations", "elements": []}

        for item in details.get("items", [])[:10]:
            element = {
                "failureReason": item.get("failureReason", ""),
                "animation": item.get("animation", ""),
            }

            if "node" in item:
                node = item["node"]
                element["selector"] = node.get("selector", "")
                element["snippet"] = node.get("snippet", "")[:300]

            result["elements"].append(element)

        return result

    def _extract_dom_size(self, details: dict) -> dict:
        """Extract DOM size statistics."""
        result = {"type": "dom-size", "stats": {}}

        for item in details.get("items", []):
            stat_type = item.get("statistic", "")
            result["stats"][stat_type] = {
                "value": item.get("value"),
                "element": item.get("node", {}).get("selector", "") if item.get("node") else "",
            }

        return result

    def _extract_bootup_time(self, details: dict) -> dict:
        """Extract script evaluation/bootup time."""
        result = {"type": "bootup-time", "scripts": []}

        for item in details.get("items", [])[:15]:
            script = {
                "url": item.get("url", ""),
                "total": item.get("total"),
                "scripting": item.get("scripting"),
                "scriptParseCompile": item.get("scriptParseCompile"),
            }
            result["scripts"].append(script)

        result["total_time"] = sum(s.get("total", 0) for s in result["scripts"])
        return result

    def _extract_duplicated_js(self, details: dict) -> dict:
        """Extract duplicated JavaScript modules."""
        result = {"type": "duplicated-js", "modules": []}

        for item in details.get("items", [])[:15]:
            module = {
                "source": item.get("source", ""),
                "wastedBytes": item.get("wastedBytes", 0),
            }

            if "subItems" in item and item["subItems"].get("items"):
                module["locations"] = [sub.get("url", "") for sub in item["subItems"]["items"][:5]]

            result["modules"].append(module)

        result["total_wasted"] = details.get("overallSavingsBytes", 0)
        return result

    def _extract_lcp_details(self, details: dict) -> dict:
        """Extract LCP element lazy loading issues."""
        result = {"type": "lcp-lazy", "elements": []}

        for item in details.get("items", [])[:5]:
            element = {
                "url": item.get("url", ""),
            }

            if "node" in item:
                node = item["node"]
                element["selector"] = node.get("selector", "")
                element["snippet"] = node.get("snippet", "")[:400]

            result["elements"].append(element)

        return result

    def _extract_lcp_element(self, details: dict) -> dict:
        """Extract LCP element details."""
        result = {"type": "lcp-element", "element": None}

        items = details.get("items", [])
        if items:
            item = items[0]
            result["element"] = {
                "url": item.get("url", ""),
            }

            if "node" in item:
                node = item["node"]
                result["element"]["selector"] = node.get("selector", "")
                result["element"]["snippet"] = node.get("snippet", "")[:400]
                result["element"]["nodeLabel"] = node.get("nodeLabel", "")

        return result

    def _extract_contrast_issues(self, details: dict) -> dict:
        """Extract color contrast accessibility issues."""
        result = {"type": "contrast", "elements": []}

        for item in details.get("items", [])[:15]:
            element = {}

            if "node" in item:
                node = item["node"]
                element["selector"] = node.get("selector", "")
                element["snippet"] = node.get("snippet", "")[:400]
                element["nodeLabel"] = node.get("nodeLabel", "")
                element["explanation"] = node.get("explanation", "")

            result["elements"].append(element)

        return result

    def _extract_element_issues(self, details: dict) -> dict:
        """Extract generic element-based accessibility issues."""
        result = {"type": "element-issues", "elements": []}

        for item in details.get("items", [])[:15]:
            element = {}

            if "node" in item:
                node = item["node"]
                element["selector"] = node.get("selector", "")
                element["snippet"] = node.get("snippet", "")[:400]
                element["nodeLabel"] = node.get("nodeLabel", "")
                element["explanation"] = node.get("explanation", "")

            result["elements"].append(element)

        return result

    def _extract_tap_target_issues(self, details: dict) -> dict:
        """Extract tap target sizing issues."""
        result = {"type": "tap-targets", "elements": []}

        for item in details.get("items", [])[:15]:
            element = {
                "size": item.get("size", ""),
                "overlappingTarget": {},
            }

            if "tapTarget" in item:
                tap = item["tapTarget"]
                element["selector"] = tap.get("selector", "")
                element["snippet"] = tap.get("snippet", "")[:300]

            if "overlappingTarget" in item:
                overlap = item["overlappingTarget"]
                element["overlappingTarget"] = {
                    "selector": overlap.get("selector", ""),
                    "snippet": overlap.get("snippet", "")[:200],
                }

            result["elements"].append(element)

        return result

    def _trim_details(self, details: dict) -> dict:
        """Trim details while preserving ALL important diagnostic data for AI analysis."""
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

        # Keep debugData for additional context
        if "debugData" in details:
            debug = details["debugData"]
            trimmed["debugData"] = {
                "type": debug.get("type"),
                "impact": debug.get("impact"),
            }
            # Keep script attribution data
            if "manifestValue" in debug:
                trimmed["debugData"]["manifestValue"] = debug["manifestValue"]

        # Keep ALL items with comprehensive fields (increased limit for better analysis)
        if "items" in details:
            trimmed_items = []
            for item in details["items"][:30]:  # Increased to 30 for comprehensive analysis
                trimmed_item = {}

                # Keep all important metric fields
                important_keys = [
                    "url", "totalBytes", "wastedBytes", "wastedMs", "cacheLifetimeMs",
                    "cacheHitProbability", "score", "transferSize", "resourceSize",
                    "label", "groupLabel", "requestCount", "mainThreadTime",
                    "startTime", "duration", "transferSizeInKb", "blockingTime",
                    "tbtImpact", "cumulativeLayoutShiftMainFrame", "contribution"
                ]
                for key in important_keys:
                    if key in item:
                        trimmed_item[key] = item[key]

                # Handle node (DOM element) data - CRITICAL for accessibility/CLS issues
                if "node" in item:
                    node = item["node"]
                    trimmed_item["node"] = {
                        "selector": node.get("selector", "")[:400],
                        "snippet": node.get("snippet", "")[:600],
                        "nodeLabel": node.get("nodeLabel", "")[:250],
                        "boundingRect": node.get("boundingRect"),  # For CLS diagnosis
                        "path": node.get("path", "")[:200],  # DOM path
                    }

                # Handle source location (for JS/CSS issues)
                if "source" in item:
                    source = item["source"]
                    if isinstance(source, dict):
                        trimmed_item["source"] = {
                            "url": source.get("url", "")[:300],
                            "line": source.get("line"),
                            "column": source.get("column"),
                        }
                    else:
                        trimmed_item["source"] = str(source)[:300]

                # Handle entity data (third-party resources)
                if "entity" in item:
                    trimmed_item["entity"] = item["entity"]

                # Handle subItems (nested resources)
                if "subItems" in item and item["subItems"].get("items"):
                    sub_items = []
                    for sub in item["subItems"]["items"][:10]:
                        sub_item = {}
                        for key in ["url", "transferSize", "resourceSize", "blockingTime", "mainThreadTime"]:
                            if key in sub:
                                sub_item[key] = sub[key]
                        if sub_item:
                            sub_items.append(sub_item)
                    if sub_items:
                        trimmed_item["subItems"] = sub_items

                if trimmed_item:
                    trimmed_items.append(trimmed_item)

            trimmed["items"] = trimmed_items
            trimmed["total_items"] = len(details["items"])
            if len(details["items"]) > 30:
                trimmed["items_truncated"] = True
                trimmed["total_items_in_audit"] = len(details["items"])

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
