"""
Lighthouse CLI Service for SEO Audits.

This service runs Google Lighthouse audits via CLI (subprocess) to get:
- Performance scores
- SEO scores
- Accessibility scores
- Best Practices scores
- Core Web Vitals (LCP, FID/INP, CLS, FCP, TTFB)

Benefits over PageSpeed API:
- UNLIMITED audits (no API limits)
- Works on JavaScript-rendered pages
- Full control over audit settings
- Can audit staging/localhost URLs
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import logging
from typing import Optional
from pathlib import Path

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class LighthouseService:
    """
    Service for running Lighthouse audits via CLI.

    Prerequisites:
    - Node.js installed
    - Lighthouse CLI: npm install -g lighthouse
    - Chrome/Chromium installed
    """

    # Lighthouse audit categories
    CATEGORIES = [
        "performance",
        "accessibility",
        "best-practices",
        "seo",
    ]

    # Core Web Vitals metric mappings
    CWV_METRICS = {
        "largest-contentful-paint": "lcp",
        "first-input-delay": "fid",
        "interaction-to-next-paint": "inp",
        "cumulative-layout-shift": "cls",
        "first-contentful-paint": "fcp",
        "time-to-first-byte": "ttfb",
        "speed-index": "si",
        "total-blocking-time": "tbt",
    }

    def __init__(self, site_audit=None):
        """
        Initialize Lighthouse service.

        Args:
            site_audit: Optional SiteAudit model instance
        """
        self.site_audit = site_audit
        self.chrome_flags = [
            "--headless=new",
            "--no-sandbox",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--disable-software-rasterizer",
            "--ignore-certificate-errors",
            "--disable-extensions",
            "--disable-background-networking",
            "--disable-sync",
            "--disable-translate",
            "--metrics-recording-only",
            "--mute-audio",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
        ]

    def check_lighthouse_installed(self) -> bool:
        """Check if Lighthouse CLI is installed."""
        try:
            result = subprocess.run(
                ["lighthouse", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def run_audit(self) -> dict:
        """
        Run full site audit for all target URLs.

        Returns:
            dict with audit results and statistics
        """
        from ..models import SiteAudit, PageAudit, AuditIssue

        if not self.site_audit:
            return {"success": False, "error": "No site audit configured"}

        # Update status
        self.site_audit.status = SiteAudit.STATUS_RUNNING
        self.site_audit.started_at = timezone.now()
        self.site_audit.save(update_fields=["status", "started_at"])

        results = {
            "success": True,
            "pages_audited": 0,
            "total_issues": 0,
            "critical_issues": 0,
            "warning_issues": 0,
            "page_results": [],
            "errors": [],
        }

        urls = self.site_audit.target_urls or [f"https://{self.site_audit.domain}/"]

        for url in urls:
            try:
                page_result = self.audit_page(
                    url=url,
                    strategy=self.site_audit.strategy
                )

                if page_result.get("success"):
                    # Create PageAudit record
                    page_audit = PageAudit.objects.create(
                        site_audit=self.site_audit,
                        url=url,
                        strategy=self.site_audit.strategy,
                        performance_score=page_result.get("performance_score"),
                        accessibility_score=page_result.get("accessibility_score"),
                        best_practices_score=page_result.get("best_practices_score"),
                        seo_score=page_result.get("seo_score"),
                        lcp=page_result.get("lcp"),
                        fid=page_result.get("fid"),
                        inp=page_result.get("inp"),
                        cls=page_result.get("cls"),
                        fcp=page_result.get("fcp"),
                        ttfb=page_result.get("ttfb"),
                        si=page_result.get("si"),
                        tbt=page_result.get("tbt"),
                        raw_data=page_result.get("raw_data", {}),
                        status="completed",
                    )

                    # Create AuditIssue records
                    for issue_data in page_result.get("issues", []):
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

                        results["total_issues"] += 1
                        if issue_data.get("severity") == "error":
                            results["critical_issues"] += 1
                        elif issue_data.get("severity") == "warning":
                            results["warning_issues"] += 1

                    results["pages_audited"] += 1
                    results["page_results"].append({
                        "url": url,
                        "scores": {
                            "performance": page_result.get("performance_score"),
                            "seo": page_result.get("seo_score"),
                            "accessibility": page_result.get("accessibility_score"),
                            "best_practices": page_result.get("best_practices_score"),
                        }
                    })
                else:
                    results["errors"].append({
                        "url": url,
                        "error": page_result.get("error", "Unknown error")
                    })

            except Exception as e:
                logger.exception(f"Error auditing {url}")
                results["errors"].append({
                    "url": url,
                    "error": str(e)
                })

        # Calculate averages
        page_audits = self.site_audit.page_audits.all()
        if page_audits.exists():
            self.site_audit.avg_performance = self._calculate_avg(page_audits, "performance_score")
            self.site_audit.avg_seo = self._calculate_avg(page_audits, "seo_score")
            self.site_audit.avg_accessibility = self._calculate_avg(page_audits, "accessibility_score")
            self.site_audit.avg_best_practices = self._calculate_avg(page_audits, "best_practices_score")

        # Update final status
        self.site_audit.status = SiteAudit.STATUS_COMPLETED
        self.site_audit.completed_at = timezone.now()
        self.site_audit.total_pages = results["pages_audited"]
        self.site_audit.total_issues = results["total_issues"]
        self.site_audit.critical_issues = results["critical_issues"]
        self.site_audit.warning_issues = results["warning_issues"]
        self.site_audit.save()

        return results

    def audit_page(self, url: str, strategy: str = "mobile") -> dict:
        """
        Run Lighthouse audit for a single page.

        Args:
            url: URL to audit
            strategy: "mobile" or "desktop"

        Returns:
            dict with audit results
        """
        result = {
            "success": False,
            "url": url,
            "strategy": strategy,
        }

        # Check if Lighthouse is available
        if not self.check_lighthouse_installed():
            result["error"] = "Lighthouse CLI not installed. Run: npm install -g lighthouse"
            return result

        try:
            with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
                output_path = tmp.name

            # Build Lighthouse command
            cmd = [
                "lighthouse",
                url,
                f"--output=json",
                f"--output-path={output_path}",
                f"--chrome-flags={' '.join(self.chrome_flags)}",
                "--quiet",
            ]

            # Add form factor
            if strategy == "mobile":
                cmd.append("--form-factor=mobile")
                cmd.append("--screenEmulation.mobile")
            else:
                cmd.append("--form-factor=desktop")
                cmd.append("--screenEmulation.disabled")

            # Run Lighthouse
            logger.info(f"Running Lighthouse audit for {url}")
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

            if process.returncode != 0:
                result["error"] = f"Lighthouse failed: {process.stderr[:500]}"
                return result

            # Parse results
            with open(output_path, "r") as f:
                lighthouse_data = json.load(f)

            # Extract scores (0-100)
            categories = lighthouse_data.get("categories", {})
            result["performance_score"] = self._extract_score(categories.get("performance"))
            result["accessibility_score"] = self._extract_score(categories.get("accessibility"))
            result["best_practices_score"] = self._extract_score(categories.get("best-practices"))
            result["seo_score"] = self._extract_score(categories.get("seo"))

            # Extract Core Web Vitals
            audits = lighthouse_data.get("audits", {})
            cwv = self._extract_cwv(audits)
            result.update(cwv)

            # Extract issues
            result["issues"] = self._extract_issues(lighthouse_data)

            # Store raw data (trimmed)
            result["raw_data"] = self._trim_raw_data(lighthouse_data)

            result["success"] = True

            # Cleanup
            Path(output_path).unlink(missing_ok=True)

        except subprocess.TimeoutExpired:
            result["error"] = "Lighthouse audit timed out (>2 minutes)"
        except json.JSONDecodeError as e:
            result["error"] = f"Failed to parse Lighthouse output: {e}"
        except Exception as e:
            result["error"] = str(e)
            logger.exception(f"Error running Lighthouse for {url}")

        return result

    def _extract_score(self, category_data: Optional[dict]) -> Optional[int]:
        """Extract score from category data (0-100)."""
        if not category_data:
            return None
        score = category_data.get("score")
        if score is not None:
            return int(score * 100)
        return None

    def _extract_cwv(self, audits: dict) -> dict:
        """Extract Core Web Vitals metrics."""
        cwv = {}

        # LCP (in seconds)
        lcp_audit = audits.get("largest-contentful-paint", {})
        if lcp_audit.get("numericValue"):
            cwv["lcp"] = lcp_audit["numericValue"] / 1000  # ms to seconds

        # FCP (in seconds)
        fcp_audit = audits.get("first-contentful-paint", {})
        if fcp_audit.get("numericValue"):
            cwv["fcp"] = fcp_audit["numericValue"] / 1000

        # CLS
        cls_audit = audits.get("cumulative-layout-shift", {})
        if cls_audit.get("numericValue") is not None:
            cwv["cls"] = cls_audit["numericValue"]

        # TBT (in milliseconds)
        tbt_audit = audits.get("total-blocking-time", {})
        if tbt_audit.get("numericValue"):
            cwv["tbt"] = tbt_audit["numericValue"]

        # Speed Index (in seconds)
        si_audit = audits.get("speed-index", {})
        if si_audit.get("numericValue"):
            cwv["si"] = si_audit["numericValue"] / 1000

        # TTFB (in milliseconds)
        ttfb_audit = audits.get("server-response-time", {})
        if ttfb_audit.get("numericValue"):
            cwv["ttfb"] = ttfb_audit["numericValue"]

        # INP (in milliseconds) - may not be available in all Lighthouse versions
        inp_audit = audits.get("interaction-to-next-paint", {})
        if inp_audit.get("numericValue"):
            cwv["inp"] = inp_audit["numericValue"]

        return cwv

    def _extract_issues(self, lighthouse_data: dict) -> list:
        """Extract issues/opportunities from Lighthouse report."""
        issues = []
        audits = lighthouse_data.get("audits", {})
        categories = lighthouse_data.get("categories", {})

        # Map audit IDs to categories
        audit_to_category = {}
        for cat_id, cat_data in categories.items():
            for audit_ref in cat_data.get("auditRefs", []):
                audit_to_category[audit_ref.get("id")] = cat_id

        for audit_id, audit_data in audits.items():
            # Skip informational/passed audits
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

        return result[:20]

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

    def _format_cache_ttl(self, ms) -> str:
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
            element = {"url": item.get("url", "")}

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
            result["element"] = {"url": item.get("url", "")}

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

        trimmed = {
            "type": details.get("type"),
        }

        # Keep headings for understanding column structure
        if "headings" in details:
            trimmed["headings"] = details["headings"]

        # Keep summary data
        if "summary" in details:
            trimmed["summary"] = details["summary"]

        # Keep overall savings
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
            if "manifestValue" in debug:
                trimmed["debugData"]["manifestValue"] = debug["manifestValue"]

        # Keep ALL items with comprehensive fields (increased limit for better analysis)
        if "items" in details:
            trimmed_items = []
            for item in details["items"][:30]:  # Increased to 30 for comprehensive analysis
                trimmed_item = {}

                # Keep all important metric fields
                important_keys = [
                    "url", "requestUrl", "totalBytes", "wastedBytes", "wastedMs",
                    "wastedPercent", "cacheLifetimeMs", "cacheHitProbability",
                    "score", "transferSize", "resourceSize", "resourceType", "mimeType",
                    "label", "groupLabel", "requestCount", "mainThreadTime",
                    "startTime", "duration", "blockingTime", "tbtImpact",
                    "cumulativeLayoutShiftMainFrame", "contribution"
                ]
                for key in important_keys:
                    if key in item:
                        trimmed_item[key] = item[key]

                # DOM element information - CRITICAL for CLS, accessibility
                if "node" in item:
                    node = item["node"]
                    trimmed_item["node"] = {
                        "type": node.get("type"),
                        "selector": node.get("selector", "")[:400],
                        "snippet": node.get("snippet", "")[:600],
                        "nodeLabel": node.get("nodeLabel", "")[:250],
                        "boundingRect": node.get("boundingRect"),  # For CLS diagnosis
                        "path": node.get("path", "")[:200],
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

    def _trim_raw_data(self, lighthouse_data: dict) -> dict:
        """Trim raw Lighthouse data for storage."""
        return {
            "lighthouseVersion": lighthouse_data.get("lighthouseVersion"),
            "fetchTime": lighthouse_data.get("fetchTime"),
            "requestedUrl": lighthouse_data.get("requestedUrl"),
            "finalUrl": lighthouse_data.get("finalUrl"),
            "runWarnings": lighthouse_data.get("runWarnings", []),
            "configSettings": {
                "formFactor": lighthouse_data.get("configSettings", {}).get("formFactor"),
                "screenEmulation": lighthouse_data.get("configSettings", {}).get("screenEmulation"),
            },
        }

    def _calculate_avg(self, queryset, field: str) -> Optional[float]:
        """Calculate average of a field across queryset."""
        values = [getattr(obj, field) for obj in queryset if getattr(obj, field) is not None]
        if values:
            return sum(values) / len(values)
        return None


def run_quick_audit(url: str, strategy: str = "mobile") -> dict:
    """
    Convenience function to run a quick single-page audit.

    Args:
        url: URL to audit
        strategy: "mobile" or "desktop"

    Returns:
        dict with audit results
    """
    service = LighthouseService()
    return service.audit_page(url, strategy)
