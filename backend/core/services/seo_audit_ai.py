"""
SEO Audit AI Engine.

This service uses ChatGPT to analyze audit results and generate:
- Prioritized fix recommendations
- Technical implementation guidance
- Django/React specific optimizations
- Impact assessments
- Executive summaries
"""

from __future__ import annotations

import json
import logging
from typing import Optional

from django.conf import settings

from .ai_client import AIContentEngine

logger = logging.getLogger(__name__)


class SEOAuditAIEngine:
    """
    AI-powered analysis engine for SEO audit results.

    Uses ChatGPT to transform raw audit data into actionable insights.
    """

    SYSTEM_PROMPT = """You are an expert SEO specialist analyzing technical audit data
for Codeteki, a company running a Django backend with React.js frontend (Single Page Application)
served from a single server.

PROJECT STRUCTURE:
- Backend: Django 4.x at /backend/
- Frontend: React at /frontend/src/ with .jsx file extensions (NOT .js)
- Components: /frontend/src/components/*.jsx
- Pages: /frontend/src/pages/*.jsx
- Static files served via WhiteNoise with content hashing

Your role is to:
1. Analyze audit issues and prioritize them by impact
2. Provide specific, actionable fix recommendations
3. Include code examples when applicable (Django/Python, React/JavaScript)
4. Consider the SPA architecture when suggesting fixes
5. Focus on Core Web Vitals and SEO best practices

IMPORTANT RULES:
- Use .jsx extension for React components (NOT .js)
- Reference bundled file URLs exactly as shown in the audit data
- Do NOT guess source file paths if you don't know them - reference the bundled files instead
- Be specific about which bundled files (main.xxx.js, xxx.chunk.js) need attention

Always format your responses with clear sections and bullet points."""

    def __init__(self, site_audit=None, ai_engine: Optional[AIContentEngine] = None):
        """
        Initialize the audit AI engine.

        Args:
            site_audit: SiteAudit model instance to analyze
            ai_engine: Optional AIContentEngine instance
        """
        self.site_audit = site_audit
        self.ai = ai_engine or AIContentEngine()

    def analyze(self) -> dict:
        """
        Generate comprehensive AI analysis of audit results.

        Returns:
            dict with analysis results
        """
        if not self.site_audit:
            return {"success": False, "error": "No site audit provided"}

        if not self.ai.enabled:
            return {"success": False, "error": "AI engine not enabled"}

        result = {"success": False}

        try:
            # Gather audit data
            audit_data = self._gather_audit_data()

            # Generate analysis
            prompt = self._build_analysis_prompt(audit_data)
            response = self.ai.generate(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT,
                temperature=0.3,
            )

            if response.get("success"):
                analysis = response.get("output", "")

                # Post-process to fix escaped newlines in code blocks
                analysis = SEOAuditAIEngine._fix_markdown_formatting(analysis)

                # Save to site audit
                self.site_audit.ai_analysis = analysis
                self.site_audit.save(update_fields=["ai_analysis", "updated_at"])

                result["success"] = True
                result["analysis"] = analysis
                result["tokens"] = response.get("usage", {})
            else:
                result["error"] = response.get("error", "AI generation failed")

        except Exception as e:
            result["error"] = str(e)
            logger.exception("Error generating audit analysis")

        return result

    def generate_fix_recommendations(self) -> dict:
        """
        Generate specific fix recommendations for audit issues.

        Returns:
            dict with recommendations
        """
        from ..models import AuditIssue, SEORecommendation

        if not self.site_audit:
            return {"success": False, "error": "No site audit provided"}

        result = {
            "success": False,
            "recommendations_created": 0,
        }

        try:
            # Get critical and warning issues
            issues = AuditIssue.objects.filter(
                page_audit__site_audit=self.site_audit,
                severity__in=["error", "warning"],
            ).select_related("page_audit")[:20]  # Limit to top 20

            for issue in issues:
                rec_result = self._generate_issue_recommendation(issue)
                if rec_result.get("success"):
                    result["recommendations_created"] += 1

            result["success"] = True

        except Exception as e:
            result["error"] = str(e)
            logger.exception("Error generating fix recommendations")

        return result

    def _generate_issue_recommendation(self, issue) -> dict:
        """Generate recommendation for a single issue."""
        from ..models import SEORecommendation

        prompt = f"""Analyze this Lighthouse audit issue and provide a fix recommendation.

ISSUE: {issue.title}
DESCRIPTION: {issue.description}
CATEGORY: {issue.category}
SEVERITY: {issue.severity}
AFFECTED URL: {issue.page_audit.url}
CURRENT SCORE: {issue.score}
POTENTIAL SAVINGS: {issue.savings_ms}ms / {issue.savings_bytes} bytes

SITE ARCHITECTURE:
- Django 4.x backend
- React.js SPA frontend
- WhiteNoise for static files
- Single server deployment

Provide:
1. PRIORITY LEVEL: critical/high/medium/low
2. ESTIMATED IMPACT: How much will fixing this improve scores?
3. FIX INSTRUCTIONS: Step-by-step instructions
4. CODE EXAMPLE: Specific code changes if applicable
5. ESTIMATED TIME: How long to implement

Format as JSON:
{{
    "priority": "high",
    "impact": "Description of expected impact",
    "fix_instructions": ["Step 1", "Step 2"],
    "code_example": "Optional code snippet",
    "estimated_time": "30 minutes",
    "reasoning": "Why this fix is important"
}}"""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.2,
        )

        if not response.get("success"):
            return {"success": False, "error": response.get("error")}

        try:
            # Parse JSON response
            output = response.get("output", "")
            # Try to extract JSON from response
            json_start = output.find("{")
            json_end = output.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                rec_data = json.loads(output[json_start:json_end])
            else:
                rec_data = {"priority": "medium", "reasoning": output}

            # Create recommendation
            SEORecommendation.objects.create(
                upload=None,
                audit_issue=issue,
                target_url=issue.page_audit.url,
                target_field=issue.audit_id,
                recommendation_type=SEORecommendation.TYPE_TECHNICAL_FIX,
                title=f"Fix: {issue.title}",
                current_value=issue.display_value or str(issue.score),
                recommended_value=json.dumps(rec_data.get("fix_instructions", []), indent=2),
                reasoning=rec_data.get("reasoning", ""),
                priority=rec_data.get("priority", "medium"),
                status=SEORecommendation.STATUS_GENERATED,
                ai_model=self.ai.model,
                ai_tokens_used=response.get("usage", {}).get("completion_tokens", 0),
            )

            # Update issue with AI recommendation
            issue.ai_fix_recommendation = output
            issue.save(update_fields=["ai_fix_recommendation", "updated_at"])

            return {"success": True}

        except json.JSONDecodeError:
            # Save raw response if not valid JSON
            SEORecommendation.objects.create(
                audit_issue=issue,
                target_url=issue.page_audit.url,
                recommendation_type=SEORecommendation.TYPE_TECHNICAL_FIX,
                title=f"Fix: {issue.title}",
                recommended_value=response.get("output", ""),
                priority="medium",
                ai_model=self.ai.model,
            )
            return {"success": True}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _gather_audit_data(self) -> dict:
        """Gather comprehensive audit data for analysis."""
        from ..models import PageAudit, AuditIssue

        page_audits = self.site_audit.page_audits.all()

        data = {
            "site_audit": {
                "name": self.site_audit.name,
                "domain": self.site_audit.domain,
                "strategy": self.site_audit.strategy,
                "total_pages": self.site_audit.total_pages,
                "total_issues": self.site_audit.total_issues,
                "critical_issues": self.site_audit.critical_issues,
                "avg_performance": self.site_audit.avg_performance,
                "avg_seo": self.site_audit.avg_seo,
                "avg_accessibility": self.site_audit.avg_accessibility,
                "avg_best_practices": self.site_audit.avg_best_practices,
            },
            "pages": [],
            "issues_by_category": {
                "performance": [],
                "seo": [],
                "accessibility": [],
                "best-practices": [],
            },
            "core_web_vitals": [],
        }

        # Add page data with all metrics
        for page in page_audits[:10]:
            page_data = {
                "url": page.url,
                "performance": page.performance_score,
                "seo": page.seo_score,
                "accessibility": page.accessibility_score,
                "best_practices": page.best_practices_score,
                "lcp": page.lcp,
                "cls": page.cls,
                "tbt": page.tbt,
                "fcp": page.fcp,
                "si": page.si,
            }
            data["pages"].append(page_data)

            # Add to Core Web Vitals summary
            data["core_web_vitals"].append({
                "url": page.url,
                "lcp": {"value": page.lcp, "status": "good" if page.lcp and page.lcp <= 2.5 else "needs improvement" if page.lcp and page.lcp <= 4 else "poor"},
                "cls": {"value": page.cls, "status": "good" if page.cls and page.cls <= 0.1 else "needs improvement" if page.cls and page.cls <= 0.25 else "poor"},
                "tbt": {"value": page.tbt, "status": "good" if page.tbt and page.tbt <= 200 else "needs improvement" if page.tbt and page.tbt <= 600 else "poor"},
            })

        # Add detailed issues with full context
        issues = AuditIssue.objects.filter(
            page_audit__site_audit=self.site_audit,
            severity__in=["error", "warning"],
        ).select_related("page_audit").order_by("severity", "-savings_ms")[:30]

        for issue in issues:
            issue_data = {
                "audit_id": issue.audit_id,
                "title": issue.title,
                "description": issue.description[:500] if issue.description else "",
                "category": issue.category,
                "severity": issue.severity,
                "url": issue.page_audit.url,
                "score": issue.score,
                "display_value": issue.display_value,
                "savings_ms": issue.savings_ms,
                "savings_bytes": issue.savings_bytes,
                # Include detailed data for specific analysis
                "details": self._extract_important_details(issue.details) if issue.details else None,
            }

            # Add to category-specific list
            category = issue.category
            if category in data["issues_by_category"]:
                data["issues_by_category"][category].append(issue_data)

        return data

    def _extract_important_details(self, details: dict) -> dict:
        """Extract important details from Lighthouse issue data - COMPREHENSIVE version."""
        if not details:
            return {}

        extracted = {}

        # Extract type for context
        if "type" in details:
            extracted["type"] = details["type"]

        # Extract overall savings
        if "overallSavingsMs" in details:
            extracted["total_savings_ms"] = round(details["overallSavingsMs"], 1)
        if "overallSavingsBytes" in details:
            extracted["total_savings_kb"] = round(details["overallSavingsBytes"] / 1024, 1)

        # Extract items/resources if present - KEEP ALL ITEMS for thorough analysis
        if "items" in details:
            items = details["items"]  # Keep ALL items, not just first 15
            extracted["affected_resources"] = []

            for item in items[:25]:  # Increased limit for more context
                resource = {}

                # URL/Source - the most important field
                if "url" in item:
                    resource["file"] = item["url"]

                # Size metrics
                if "totalBytes" in item:
                    resource["total_size"] = f"{round(item['totalBytes'] / 1024, 1)} KB"
                if "wastedBytes" in item:
                    resource["wasted"] = f"{round(item['wastedBytes'] / 1024, 1)} KB"
                if "wastedMs" in item:
                    resource["time_wasted"] = f"{round(item['wastedMs'])} ms"
                if "transferSize" in item:
                    resource["transfer_size"] = f"{round(item['transferSize'] / 1024, 1)} KB"

                # Cache info - critical for cache issues
                if "cacheLifetimeMs" in item:
                    cache_ms = item["cacheLifetimeMs"]
                    if cache_ms == 0:
                        resource["cache_policy"] = "NO CACHE (must fix!)"
                    elif cache_ms < 3600000:  # Less than 1 hour
                        resource["cache_policy"] = f"{round(cache_ms / 60000)} minutes"
                    elif cache_ms < 86400000:  # Less than 1 day
                        resource["cache_policy"] = f"{round(cache_ms / 3600000, 1)} hours"
                    else:
                        resource["cache_policy"] = f"{round(cache_ms / 86400000)} days"

                # DOM element info - critical for CLS/accessibility
                if "node" in item:
                    node = item["node"]
                    if node.get("snippet"):
                        resource["html_element"] = node["snippet"][:400]
                    if node.get("selector"):
                        resource["css_selector"] = node["selector"]
                    if node.get("nodeLabel"):
                        resource["element_label"] = node["nodeLabel"]
                    if node.get("boundingRect"):
                        rect = node["boundingRect"]
                        resource["element_size"] = f"{rect.get('width', 0)}x{rect.get('height', 0)}px"

                # CLS specific data
                if "cumulativeLayoutShiftMainFrame" in item:
                    resource["cls_contribution"] = round(item["cumulativeLayoutShiftMainFrame"], 4)
                if "score" in item and isinstance(item["score"], (int, float)):
                    resource["impact_score"] = round(item["score"] * 100)

                # Label/description
                if "label" in item:
                    resource["description"] = item["label"]
                if "groupLabel" in item:
                    resource["group"] = item["groupLabel"]

                # Source location for JS/CSS
                if "source" in item:
                    source = item["source"]
                    if isinstance(source, dict):
                        source_info = source.get("url", "")
                        if source.get("line"):
                            source_info += f" (line {source['line']})"
                        resource["source_location"] = source_info
                    else:
                        resource["source_location"] = str(source)

                # Sub-items (nested resources)
                if "subItems" in item and item["subItems"].get("items"):
                    sub_resources = []
                    for sub in item["subItems"]["items"][:5]:
                        sub_info = {}
                        if "url" in sub:
                            sub_info["file"] = sub["url"]
                        if "transferSize" in sub:
                            sub_info["size"] = f"{round(sub['transferSize'] / 1024, 1)} KB"
                        if sub_info:
                            sub_resources.append(sub_info)
                    if sub_resources:
                        resource["sub_resources"] = sub_resources

                if resource:
                    extracted["affected_resources"].append(resource)

            # Count info
            extracted["total_resources_affected"] = len(details["items"])
            if len(details["items"]) > 25:
                extracted["note"] = f"Showing 25 of {len(details['items'])} affected resources"

        # Extract headings for table context
        if "headings" in details:
            extracted["data_columns"] = [h.get("label", h.get("key", "")) for h in details["headings"][:8]]

        # Extract summary
        if "summary" in details:
            extracted["summary"] = details["summary"]

        # Extract debugData if present (contains useful diagnostic info)
        if "debugData" in details:
            debug = details["debugData"]
            if "type" in debug:
                extracted["debug_type"] = debug["type"]
            if "impact" in debug:
                extracted["impact"] = debug["impact"]

        return extracted if extracted else None

    @classmethod
    def generate_combined_analysis(cls, site_audits, save_to=None) -> dict:
        """
        Generate comprehensive AI analysis combining multiple data sources.

        Args:
            site_audits: QuerySet or list of SiteAudit instances
            save_to: Optional SiteAudit to save the combined analysis to

        Returns:
            dict with combined analysis results
        """
        from ..models import PageAudit, AuditIssue, PageSpeedResult, SearchConsoleData

        ai_engine = AIContentEngine()
        if not ai_engine.enabled:
            return {"success": False, "error": "AI engine not enabled"}

        result = {"success": False}

        try:
            # Collect domains from all audits
            domains = set()
            combined_data = {
                "audits_summary": [],
                "all_pages": [],
                "all_issues": [],
                "pagespeed_data": [],
                "search_console_data": [],
            }

            # Gather data from all Site Audits
            for audit in site_audits:
                domains.add(audit.domain)
                combined_data["audits_summary"].append({
                    "name": audit.name,
                    "domain": audit.domain,
                    "strategy": audit.strategy,
                    "date": audit.created_at.strftime("%Y-%m-%d"),
                    "avg_performance": audit.avg_performance,
                    "avg_seo": audit.avg_seo,
                    "avg_accessibility": audit.avg_accessibility,
                    "avg_best_practices": audit.avg_best_practices,
                    "total_issues": audit.total_issues,
                    "critical_issues": audit.critical_issues,
                })

                # Add page audits
                for page in audit.page_audits.all()[:5]:
                    combined_data["all_pages"].append({
                        "url": page.url,
                        "strategy": page.strategy,
                        "performance": page.performance_score,
                        "seo": page.seo_score,
                        "accessibility": page.accessibility_score,
                        "best_practices": page.best_practices_score,
                        "lcp": page.lcp,
                        "cls": page.cls,
                        "fcp": page.fcp,
                        "tbt": page.tbt,
                        "audit_date": audit.created_at.strftime("%Y-%m-%d"),
                    })

                # Add issues
                issues = AuditIssue.objects.filter(
                    page_audit__site_audit=audit,
                    severity__in=["error", "warning"],
                ).order_by("severity", "-savings_ms")[:10]

                for issue in issues:
                    combined_data["all_issues"].append({
                        "title": issue.title,
                        "category": issue.category,
                        "severity": issue.severity,
                        "url": issue.page_audit.url,
                        "savings_ms": issue.savings_ms,
                        "display_value": issue.display_value,
                    })

            # Gather PageSpeed Results for the same domains
            for domain in domains:
                pagespeed_results = PageSpeedResult.objects.filter(
                    url__icontains=domain
                ).order_by("-created_at")[:5]

                for ps in pagespeed_results:
                    combined_data["pagespeed_data"].append({
                        "url": ps.url,
                        "strategy": ps.strategy,
                        "lab_performance_score": ps.lab_performance_score,
                        "overall_category": ps.overall_category,
                        # Lab metrics
                        "lab_lcp": ps.lab_lcp,
                        "lab_cls": ps.lab_cls,
                        "lab_fcp": ps.lab_fcp,
                        "lab_tbt": ps.lab_tbt,
                        # Field metrics (real user data)
                        "field_lcp": ps.field_lcp,
                        "field_cls": ps.field_cls,
                        "field_fcp": ps.field_fcp,
                        "field_fid": ps.field_fid,
                        "field_inp": ps.field_inp,
                        "field_ttfb": ps.field_ttfb,
                        "date": ps.created_at.strftime("%Y-%m-%d"),
                    })

            # Gather Search Console Data for the same domains
            for domain in domains:
                sc_data = SearchConsoleData.objects.filter(
                    page__icontains=domain
                ).order_by("-date")[:20]

                if sc_data.exists():
                    # Aggregate Search Console metrics
                    total_clicks = sum(d.clicks or 0 for d in sc_data)
                    total_impressions = sum(d.impressions or 0 for d in sc_data)
                    avg_position = sum(d.position or 0 for d in sc_data) / len(sc_data) if sc_data else 0
                    avg_ctr = sum(d.ctr or 0 for d in sc_data) / len(sc_data) if sc_data else 0

                    combined_data["search_console_data"].append({
                        "domain": domain,
                        "total_clicks": total_clicks,
                        "total_impressions": total_impressions,
                        "avg_position": round(avg_position, 1),
                        "avg_ctr": round(avg_ctr * 100, 2),
                        "top_queries": list(sc_data.values_list("query", flat=True).distinct()[:10]),
                    })

            # Build combined prompt
            prompt = cls._build_combined_prompt(combined_data)

            # Generate analysis
            response = ai_engine.generate(
                prompt=prompt,
                system_prompt=cls.COMBINED_SYSTEM_PROMPT,
                temperature=0.3,
            )

            if response.get("success"):
                analysis = response.get("output", "")

                # Post-process to fix escaped newlines in code blocks
                analysis = cls._fix_markdown_formatting(analysis)

                # Save to specified audit if provided
                if save_to:
                    save_to.ai_analysis = analysis
                    save_to.save(update_fields=["ai_analysis", "updated_at"])

                result["success"] = True
                result["analysis"] = analysis
                result["tokens"] = response.get("usage", {})
                result["data_sources"] = {
                    "audits": len(combined_data["audits_summary"]),
                    "pages": len(combined_data["all_pages"]),
                    "issues": len(combined_data["all_issues"]),
                    "pagespeed_results": len(combined_data["pagespeed_data"]),
                    "search_console_entries": len(combined_data["search_console_data"]),
                }
            else:
                result["error"] = response.get("error", "AI generation failed")

        except Exception as e:
            result["error"] = str(e)
            logger.exception("Error generating combined analysis")

        return result

    @staticmethod
    def _fix_markdown_formatting(text: str) -> str:
        """
        Fix common markdown formatting issues in AI-generated content.
        - Convert literal \\n to actual newlines in code blocks
        - Fix escaped characters
        """
        import re

        # Replace literal \n with actual newlines
        text = text.replace("\\n", "\n")

        # Fix double-escaped backslashes
        text = text.replace("\\\\", "\\")

        # Clean up any triple+ newlines to double newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    COMBINED_SYSTEM_PROMPT = """You are an expert SEO specialist providing a comprehensive analysis
combining data from multiple sources: Lighthouse audits, PageSpeed Insights, and Google Search Console.

Your role is to:
1. Synthesize data from multiple audits to identify patterns and trends
2. Cross-reference Lighthouse issues with PageSpeed recommendations
3. Connect technical issues to Search Console performance data
4. Prioritize fixes based on combined impact across all data sources
5. Provide Django/React specific implementation guidance

Format your response with clear sections, bullet points, and code examples where applicable.
Focus on actionable recommendations that will improve both technical SEO and user experience."""

    @classmethod
    def _build_combined_prompt(cls, data: dict) -> str:
        """Build the combined analysis prompt."""
        return f"""Analyze this comprehensive SEO data from multiple sources and provide a unified analysis:

## SITE AUDITS (Lighthouse)
{json.dumps(data['audits_summary'], indent=2)}

## PAGE-LEVEL SCORES
{json.dumps(data['all_pages'][:15], indent=2)}

## CRITICAL ISSUES FOUND
{json.dumps(data['all_issues'][:20], indent=2)}

## PAGESPEED INSIGHTS DATA
{json.dumps(data['pagespeed_data'], indent=2) if data['pagespeed_data'] else 'No PageSpeed data available'}

## SEARCH CONSOLE DATA
{json.dumps(data['search_console_data'], indent=2) if data['search_console_data'] else 'No Search Console data available'}

---

Please provide a COMPREHENSIVE COMBINED ANALYSIS:

## 1. EXECUTIVE SUMMARY
- Overall site health based on ALL data sources
- Key patterns identified across audits
- Most critical issues affecting performance AND rankings

## 2. CROSS-SOURCE INSIGHTS
- How Lighthouse issues correlate with PageSpeed findings
- Impact of technical issues on Search Console metrics
- Trends over time (if multiple audit dates)

## 3. CORE WEB VITALS DEEP DIVE
- LCP analysis with specific causes and fixes
- CLS issues and layout stability recommendations
- FID/TBT improvements for interactivity
- Compare Lighthouse vs PageSpeed measurements

## 4. SEO IMPACT ANALYSIS
- Technical issues affecting crawlability
- Content issues affecting rankings
- Mobile vs Desktop performance gaps
- Connection between page speed and search rankings

## 5. PRIORITIZED ACTION PLAN
For each fix provide:
- **Issue**: What needs fixing
- **Impact**: Expected improvement (performance + SEO)
- **Effort**: Easy/Medium/Hard
- **Dependencies**: What must be fixed first
- **Code Example**: Django/React implementation

## 6. DJANGO + REACT SPECIFIC FIXES
- WhiteNoise/static files optimization
- React bundle optimization (code splitting, lazy loading)
- SPA meta tag handling
- Server response time improvements

## 7. QUICK WINS VS LONG-TERM
**Quick Wins (< 1 day):**
- List immediate fixes

**Medium Term (1 week):**
- List moderate effort fixes

**Long Term (1+ month):**
- Architectural improvements

## 8. MONITORING PLAN
- Key metrics to track
- Recommended re-audit frequency
- Alert thresholds to set"""

    def _build_analysis_prompt(self, audit_data: dict) -> str:
        """Build a dynamic analysis prompt based on actual audit data."""

        # Get first page metrics for summary
        first_page = audit_data['pages'][0] if audit_data['pages'] else {}

        # Format performance issues with full details
        perf_issues = audit_data['issues_by_category'].get('performance', [])
        perf_section = self._format_issues_for_prompt(perf_issues)

        # Format other issues
        seo_issues = audit_data['issues_by_category'].get('seo', [])
        seo_section = self._format_issues_for_prompt(seo_issues)

        acc_issues = audit_data['issues_by_category'].get('accessibility', [])
        acc_section = self._format_issues_for_prompt(acc_issues)

        bp_issues = audit_data['issues_by_category'].get('best-practices', [])
        bp_section = self._format_issues_for_prompt(bp_issues)

        return f"""ANALYZE THIS REAL AUDIT DATA AND PROVIDE SPECIFIC, ACTIONABLE FIXES.

## SITE OVERVIEW
- Domain: {audit_data['site_audit']['domain']}
- Strategy: {audit_data['site_audit']['strategy']}
- Pages Audited: {audit_data['site_audit']['total_pages']}
- Total Issues: {audit_data['site_audit']['total_issues']}
- Critical Issues: {audit_data['site_audit']['critical_issues']}

## CURRENT SCORES (Averages)
- Performance: {audit_data['site_audit'].get('avg_performance', 'N/A')}
- SEO: {audit_data['site_audit'].get('avg_seo', 'N/A')}
- Accessibility: {audit_data['site_audit'].get('avg_accessibility', 'N/A')}
- Best Practices: {audit_data['site_audit'].get('avg_best_practices', 'N/A')}

## CORE WEB VITALS (First Page)
- LCP: {first_page.get('lcp', 'N/A')}s (target: <2.5s)
- CLS: {first_page.get('cls', 'N/A')} (target: <0.1)
- TBT: {first_page.get('tbt', 'N/A')}ms (target: <200ms)

---

## PERFORMANCE ISSUES - WITH AFFECTED FILES/ELEMENTS
{perf_section}

## SEO ISSUES - WITH AFFECTED FILES/ELEMENTS
{seo_section}

## ACCESSIBILITY ISSUES - WITH AFFECTED FILES/ELEMENTS
{acc_section}

## BEST PRACTICES ISSUES - WITH AFFECTED FILES/ELEMENTS
{bp_section}

---

CRITICAL INSTRUCTIONS FOR YOUR RESPONSE:

1. FOR EACH ISSUE: You MUST list the EXACT files/elements from "affected_resources" in your response.
   Example: "File: https://codeteki.au/static/js/main.xxx.js (wasted: 148 KB)"

2. DO NOT give generic advice like "implement code splitting". Instead say:
   "Split the code in main.xxx.js - specifically lazy load these components that are causing the 148KB waste"

3. FOR CLS ISSUES: Quote the exact HTML element and CSS selector from the data.
   Example: "Element causing shift: <footer class='bg-black...'> (selector: footer.bg-black)"

4. FOR CACHE ISSUES: List each file with its current cache policy.
   Example: "main.xxx.js has NO CACHE - add Cache-Control: max-age=31536000"

5. USE EXACT NUMBERS from the data:
   - Savings in KB (not KiB)
   - Time savings in ms
   - Current cache policies

---

Generate a report with these EXACT sections:

# Site Audit Recommendations for {audit_data['site_audit']['domain']}

## 1. CRITICAL ISSUES (Fix Immediately)

For EACH issue with severity="error", provide:
- **Issue Title**: [exact title from data]
- **Current State**: [use display_value]
- **Affected Files/Elements**:
  - [List EACH file/element from affected_resources with its metrics]
- **Potential Savings**: [X] KB, [Y] ms
- **Exact Fix**:
  ```python
  # Django fix if applicable
  ```
  ```javascript
  // React fix if applicable - use .jsx extension
  ```

## 2. QUICK WINS (30 min or less each)

| Issue | Affected Resource | Savings | Fix |
|-------|-------------------|---------|-----|
[Table with SPECIFIC files and fixes]

## 3. MEDIUM EFFORT (1-4 hours)

For each medium issue:
- **Affected Bundle/Element**: [exact from data]
- **Root Cause**: [based on the metrics]
- **Step-by-Step Fix**:
  1. [specific step with file references]
  2. [specific step with code example]

## 4. DJANGO-SPECIFIC FIXES

Address ONLY issues actually found in the data:
- Cache headers (if cache issues found)
- Static file configuration
- WhiteNoise settings

## 5. PRIORITY ACTION PLAN

| # | Issue | File/Element | Savings | Effort | Implementation |
|---|-------|--------------|---------|--------|----------------|
[Numbered by impact, with EXACT file references]

## 6. MONITORING CHECKLIST

- Target Performance: {max(80, (audit_data['site_audit'].get('avg_performance') or 50) + 20)}+ (current: {audit_data['site_audit'].get('avg_performance', 'N/A')})
- Target SEO: 100 (current: {audit_data['site_audit'].get('avg_seo', 'N/A')})
- Target Accessibility: 100 (current: {audit_data['site_audit'].get('avg_accessibility', 'N/A')})

REMEMBER: Every recommendation MUST reference specific files, elements, or metrics from the audit data. NO GENERIC ADVICE."""

    def _format_issues_for_prompt(self, issues: list) -> str:
        """Format issues with their full details for the AI prompt."""
        if not issues:
            return "No issues found in this category."

        formatted = []
        for i, issue in enumerate(issues[:15], 1):  # Top 15 issues per category
            section = f"""
### Issue {i}: {issue['title']}
- Severity: {issue['severity'].upper()}
- URL: {issue['url']}
- Display Value: {issue.get('display_value', 'N/A')}
- Score: {issue.get('score', 'N/A')}
- Potential Savings: {issue.get('savings_ms', 0)}ms, {round(issue.get('savings_bytes', 0)/1024, 1)}KB"""

            # Add detailed affected resources
            details = issue.get('details', {})
            if details:
                if details.get('total_savings_ms'):
                    section += f"\n- Total Time Savings: {details['total_savings_ms']}ms"
                if details.get('total_savings_kb'):
                    section += f"\n- Total Size Savings: {details['total_savings_kb']}KB"

                resources = details.get('affected_resources', [])
                if resources:
                    section += "\n- **Affected Resources:**"
                    for j, res in enumerate(resources[:10], 1):
                        res_line = f"\n  {j}."
                        if res.get('file'):
                            res_line += f" File: {res['file']}"
                        if res.get('wasted'):
                            res_line += f" (wasted: {res['wasted']})"
                        if res.get('time_wasted'):
                            res_line += f" ({res['time_wasted']})"
                        if res.get('cache_policy'):
                            res_line += f" [cache: {res['cache_policy']}]"
                        if res.get('html_element'):
                            res_line += f"\n     Element: {res['html_element'][:200]}"
                        if res.get('css_selector'):
                            res_line += f"\n     Selector: {res['css_selector']}"
                        section += res_line

                    if details.get('total_resources_affected', 0) > 10:
                        section += f"\n  ... and {details['total_resources_affected'] - 10} more resources"

            formatted.append(section)

        return "\n".join(formatted)


class SEOContentAIEngine:
    """
    AI engine for content-related SEO recommendations.

    Generates meta tags, content briefs, and optimization suggestions.
    """

    SYSTEM_PROMPT = """You are an SEO content specialist for Codeteki,
an AI automation company. Generate optimized content that:
- Targets relevant keywords naturally
- Maintains brand voice (confident, helpful, tech-forward)
- Follows SEO best practices
- Is compelling and actionable

Focus on B2B SaaS/automation services content."""

    def __init__(self, ai_engine: Optional[AIContentEngine] = None):
        self.ai = ai_engine or AIContentEngine()

    def generate_meta_title(self, keyword: str, page_context: str) -> dict:
        """Generate SEO-optimized meta title."""
        prompt = f"""Generate an SEO-optimized meta title.

TARGET KEYWORD: {keyword}
PAGE CONTEXT: {page_context}
BRAND: Codeteki

Requirements:
- Maximum 60 characters
- Include keyword naturally at start if possible
- Make compelling for clicks
- Add brand at end if space permits

Return ONLY the meta title, nothing else."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        return {
            "success": response.get("success", False),
            "meta_title": response.get("output", "").strip(),
            "tokens": response.get("usage", {}),
        }

    def generate_meta_description(
        self,
        keyword: str,
        page_context: str,
        current_description: str = "",
    ) -> dict:
        """Generate SEO-optimized meta description."""
        prompt = f"""Generate an SEO-optimized meta description.

TARGET KEYWORD: {keyword}
PAGE CONTEXT: {page_context}
CURRENT META: {current_description or 'None'}

Requirements:
- Maximum 155 characters
- Include target keyword naturally
- Include a call-to-action
- Make compelling for clicks

Return ONLY the meta description, nothing else."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.7,
        )

        return {
            "success": response.get("success", False),
            "meta_description": response.get("output", "").strip(),
            "tokens": response.get("usage", {}),
        }

    def generate_content_brief(self, cluster) -> dict:
        """Generate content brief for a keyword cluster."""
        from ..models import SEOKeywordCluster

        keywords = list(cluster.keywords.values_list("keyword", flat=True)[:20])

        prompt = f"""Create a content brief for an SEO-optimized article.

KEYWORD CLUSTER: {cluster.label}
PRIMARY INTENT: {cluster.intent}
KEYWORDS IN CLUSTER:
{json.dumps(keywords, indent=2)}

TOTAL SEARCH VOLUME: {cluster.avg_volume}
AVERAGE DIFFICULTY: {cluster.avg_difficulty}

Generate:
1. Suggested article title (SEO-optimized)
2. Meta description (155 chars max)
3. H2 headings outline (5-7 sections)
4. Key points to cover in each section
5. Internal linking opportunities for Codeteki
6. Call-to-action suggestions

Format as structured JSON."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.5,
        )

        return {
            "success": response.get("success", False),
            "brief": response.get("output", ""),
            "tokens": response.get("usage", {}),
        }

    def analyze_content_gaps(self, our_keywords: list, competitor_keywords: list) -> dict:
        """Analyze content gaps between our keywords and competitors."""
        prompt = f"""Perform keyword gap analysis for Codeteki:

OUR KEYWORDS (top 50):
{json.dumps(our_keywords[:50], indent=2)}

COMPETITOR KEYWORDS (top 100):
{json.dumps(competitor_keywords[:100], indent=2)}

Identify:

## 1. KEYWORD GAPS
Keywords competitors rank for that we don't.
Prioritize by search volume and relevance.

## 2. CONTENT OPPORTUNITIES
Topics competitors cover that we should create content for.

## 3. QUICK WINS
Keywords we rank for but can improve with optimization.

## 4. UNIQUE ADVANTAGES
Keywords we rank for that competitors don't (defend these).

## 5. RECOMMENDED CONTENT PLAN
Specific content pieces to create, prioritized by opportunity."""

        response = self.ai.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPT,
            temperature=0.3,
        )

        return {
            "success": response.get("success", False),
            "analysis": response.get("output", ""),
            "tokens": response.get("usage", {}),
        }
