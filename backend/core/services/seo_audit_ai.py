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

Your role is to:
1. Analyze audit issues and prioritize them by impact
2. Provide specific, actionable fix recommendations
3. Include code examples when applicable (Django/Python, React/JavaScript)
4. Consider the SPA architecture when suggesting fixes
5. Focus on Core Web Vitals and SEO best practices

Always format your responses with clear sections and bullet points.
Be specific with file paths and code examples where possible."""

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
        """Gather audit data for analysis."""
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
            },
            "pages": [],
            "top_issues": [],
        }

        # Add page data
        for page in page_audits[:10]:  # Limit to 10 pages
            data["pages"].append({
                "url": page.url,
                "performance": page.performance_score,
                "seo": page.seo_score,
                "accessibility": page.accessibility_score,
                "lcp": page.lcp,
                "cls": page.cls,
                "tbt": page.tbt,
            })

        # Add top issues
        issues = AuditIssue.objects.filter(
            page_audit__site_audit=self.site_audit,
            severity__in=["error", "warning"],
        ).order_by("severity", "-savings_ms")[:15]

        for issue in issues:
            data["top_issues"].append({
                "title": issue.title,
                "category": issue.category,
                "severity": issue.severity,
                "url": issue.page_audit.url,
                "savings_ms": issue.savings_ms,
            })

        return data

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
        """Build the analysis prompt."""
        return f"""Analyze this site audit data and provide a comprehensive SEO analysis:

SITE AUDIT SUMMARY:
{json.dumps(audit_data['site_audit'], indent=2)}

PAGE SCORES:
{json.dumps(audit_data['pages'], indent=2)}

TOP ISSUES:
{json.dumps(audit_data['top_issues'], indent=2)}

Please provide:

## 1. EXECUTIVE SUMMARY
- Overall SEO health assessment
- Key strengths and weaknesses
- Critical issues requiring immediate attention

## 2. PERFORMANCE ANALYSIS
- Core Web Vitals assessment (LCP, CLS, TBT)
- Performance bottlenecks identified
- Quick wins vs long-term improvements

## 3. SEO ISSUES BREAKDOWN
For each major issue:
- Impact on rankings
- Fix complexity (easy/medium/hard)
- Recommended priority

## 4. DJANGO/REACT SPECIFIC RECOMMENDATIONS
- Static file optimization (WhiteNoise config)
- React bundle optimization
- Server-side rendering considerations
- Meta tag handling for SPA

## 5. ACTION PLAN
Prioritized list of fixes with:
- Expected impact
- Estimated effort
- Dependencies

## 6. MONITORING RECOMMENDATIONS
What metrics to track going forward."""


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
