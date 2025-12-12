"""
SEO Audit PDF Report Generator.

Premium PDF report generation with Codeteki branding.
Designed to be better than SEMrush, Ahrefs, and other popular SEO tool reports.
"""

from __future__ import annotations

import io
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

# Codeteki Brand Colors
CODETEKI_BRAND = {
    'primary': colors.HexColor('#6366F1'),       # Indigo
    'primary_dark': colors.HexColor('#4F46E5'),  # Darker Indigo
    'secondary': colors.HexColor('#8B5CF6'),     # Purple
    'accent': colors.HexColor('#06B6D4'),        # Cyan
    'success': colors.HexColor('#10B981'),       # Green
    'warning': colors.HexColor('#F59E0B'),       # Amber
    'danger': colors.HexColor('#EF4444'),        # Red
    'info': colors.HexColor('#3B82F6'),          # Blue
    'dark': colors.HexColor('#1F2937'),          # Gray 800
    'light': colors.HexColor('#F9FAFB'),         # Gray 50
    'gray': colors.HexColor('#6B7280'),          # Gray 500
    'border': colors.HexColor('#E5E7EB'),        # Gray 200
}

# Score color mapping
def get_score_color(score: Optional[float]) -> colors.Color:
    """Get color based on score (0-100)."""
    if score is None:
        return CODETEKI_BRAND['gray']
    if score >= 90:
        return CODETEKI_BRAND['success']
    elif score >= 50:
        return CODETEKI_BRAND['warning']
    else:
        return CODETEKI_BRAND['danger']


def get_cwv_color(metric: str, value: Optional[float]) -> colors.Color:
    """Get color based on Core Web Vitals thresholds."""
    if value is None:
        return CODETEKI_BRAND['gray']

    thresholds = {
        'lcp': (2.5, 4.0),       # seconds
        'fcp': (1.8, 3.0),       # seconds
        'cls': (0.1, 0.25),      # unitless
        'tbt': (200, 600),       # milliseconds
        'fid': (100, 300),       # milliseconds
        'inp': (200, 500),       # milliseconds
        'ttfb': (800, 1800),     # milliseconds
        'si': (3.4, 5.8),        # seconds
    }

    if metric not in thresholds:
        return CODETEKI_BRAND['gray']

    good, poor = thresholds[metric]
    if value <= good:
        return CODETEKI_BRAND['success']
    elif value <= poor:
        return CODETEKI_BRAND['warning']
    else:
        return CODETEKI_BRAND['danger']


class SEOReportPDFGenerator:
    """
    Premium PDF Report Generator for SEO Audits.

    Features:
    - Codeteki branding with professional design
    - Executive summary with visual score gauges
    - Core Web Vitals dashboard
    - Issue breakdown by category and severity
    - Detailed recommendations with priority levels
    - Visual charts and graphs
    - Professional formatting rivaling SEMrush/Ahrefs
    """

    def __init__(self, site_audit):
        """
        Initialize the PDF generator.

        Args:
            site_audit: SiteAudit model instance
        """
        self.site_audit = site_audit
        self.buffer = io.BytesIO()
        self.styles = self._create_styles()
        self.logo_path = self._get_logo_path()

    def _get_logo_path(self) -> Optional[str]:
        """Get the path to the Codeteki logo."""
        possible_paths = [
            os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png'),
            os.path.join(settings.BASE_DIR, 'media', 'seo', 'codeteki_logo_copy.png'),
            os.path.join(settings.BASE_DIR, 'staticfiles', 'images', 'logo.png'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def _create_styles(self) -> dict:
        """Create custom styles for the report."""
        styles = getSampleStyleSheet()

        # Title style
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=CODETEKI_BRAND['dark'],
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        ))

        # Subtitle style
        styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=CODETEKI_BRAND['gray'],
            spaceAfter=30,
            alignment=TA_CENTER,
        ))

        # Section header style
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=CODETEKI_BRAND['primary'],
            spaceBefore=25,
            spaceAfter=15,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
        ))

        # Subsection header
        styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=CODETEKI_BRAND['dark'],
            spaceBefore=15,
            spaceAfter=10,
            fontName='Helvetica-Bold',
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=CODETEKI_BRAND['dark'],
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=14,
        ))

        # Issue title
        styles.add(ParagraphStyle(
            name='IssueTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=CODETEKI_BRAND['dark'],
            fontName='Helvetica-Bold',
            spaceAfter=4,
        ))

        # Issue description
        styles.add(ParagraphStyle(
            name='IssueDescription',
            parent=styles['Normal'],
            fontSize=9,
            textColor=CODETEKI_BRAND['gray'],
            spaceAfter=6,
            leading=12,
        ))

        # Metric value
        styles.add(ParagraphStyle(
            name='MetricValue',
            parent=styles['Normal'],
            fontSize=24,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER,
        ))

        # Metric label
        styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=CODETEKI_BRAND['gray'],
            alignment=TA_CENTER,
        ))

        # Footer text
        styles.add(ParagraphStyle(
            name='FooterText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=CODETEKI_BRAND['gray'],
            alignment=TA_CENTER,
        ))

        # Code block
        styles.add(ParagraphStyle(
            name='CodeBlock',
            parent=styles['Normal'],
            fontSize=8,
            fontName='Courier',
            backColor=CODETEKI_BRAND['light'],
            leftIndent=10,
            rightIndent=10,
            spaceAfter=10,
            leading=10,
        ))

        return styles

    def generate(self) -> bytes:
        """
        Generate the complete PDF report.

        Returns:
            PDF content as bytes
        """
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch,
        )

        # Build report elements
        elements = []

        # Cover page
        elements.extend(self._build_cover_page())
        elements.append(PageBreak())

        # Executive Summary
        elements.extend(self._build_executive_summary())
        elements.append(PageBreak())

        # Score Dashboard
        elements.extend(self._build_score_dashboard())
        elements.append(PageBreak())

        # Core Web Vitals
        elements.extend(self._build_core_web_vitals())
        elements.append(PageBreak())

        # Issues Breakdown
        elements.extend(self._build_issues_breakdown())
        elements.append(PageBreak())

        # Detailed Issues by URL
        elements.extend(self._build_issues_by_url())

        # AI Analysis (if available)
        if self.site_audit.ai_analysis:
            elements.append(PageBreak())
            elements.extend(self._build_ai_analysis())

        # Build PDF
        doc.build(elements, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)

        pdf_content = self.buffer.getvalue()
        self.buffer.close()

        return pdf_content

    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()

        # Footer
        footer_text = f"Codeteki SEO Audit Report | {self.site_audit.domain} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(CODETEKI_BRAND['gray'])
        canvas.drawCentredString(A4[0]/2, 0.4*inch, footer_text)

        # Page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(A4[0] - 0.75*inch, 0.4*inch, f"Page {page_num}")

        # Header line
        canvas.setStrokeColor(CODETEKI_BRAND['border'])
        canvas.setLineWidth(0.5)
        canvas.line(0.75*inch, A4[1] - 0.5*inch, A4[0] - 0.75*inch, A4[1] - 0.5*inch)

        canvas.restoreState()

    def _build_cover_page(self) -> list:
        """Build the cover page."""
        elements = []

        # Spacer at top
        elements.append(Spacer(1, 1.5*inch))

        # Logo
        if self.logo_path:
            try:
                logo = Image(self.logo_path, width=2*inch, height=0.6*inch)
                logo.hAlign = 'CENTER'
                elements.append(logo)
                elements.append(Spacer(1, 0.5*inch))
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")

        # Title
        elements.append(Paragraph("SEO AUDIT REPORT", self.styles['ReportTitle']))

        # Domain
        elements.append(Paragraph(
            f"<font color='{CODETEKI_BRAND['primary'].hexval()}'>{self.site_audit.domain}</font>",
            self.styles['ReportSubtitle']
        ))

        elements.append(Spacer(1, 0.5*inch))

        # Report info box
        report_info = [
            ['Report Name:', self.site_audit.name],
            ['Strategy:', self.site_audit.get_strategy_display()],
            ['Audit Date:', self.site_audit.created_at.strftime('%B %d, %Y')],
            ['Pages Analyzed:', str(self.site_audit.total_pages)],
            ['Issues Found:', str(self.site_audit.total_issues)],
        ]

        info_table = Table(report_info, colWidths=[2*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), CODETEKI_BRAND['gray']),
            ('TEXTCOLOR', (1, 0), (1, -1), CODETEKI_BRAND['dark']),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        info_table.hAlign = 'CENTER'
        elements.append(info_table)

        elements.append(Spacer(1, 1*inch))

        # Quick scores preview
        scores_data = [
            ['Performance', 'SEO', 'Accessibility', 'Best Practices'],
            [
                self._format_score(self.site_audit.avg_performance),
                self._format_score(self.site_audit.avg_seo),
                self._format_score(self.site_audit.avg_accessibility),
                self._format_score(self.site_audit.avg_best_practices),
            ]
        ]

        scores_table = Table(scores_data, colWidths=[1.4*inch]*4)
        scores_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica'),
            ('FONTNAME', (0, 1), (-1, 1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, 1), 20),
            ('TEXTCOLOR', (0, 0), (-1, 0), CODETEKI_BRAND['gray']),
            ('TEXTCOLOR', (0, 1), (0, 1), get_score_color(self.site_audit.avg_performance)),
            ('TEXTCOLOR', (1, 1), (1, 1), get_score_color(self.site_audit.avg_seo)),
            ('TEXTCOLOR', (2, 1), (2, 1), get_score_color(self.site_audit.avg_accessibility)),
            ('TEXTCOLOR', (3, 1), (3, 1), get_score_color(self.site_audit.avg_best_practices)),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, -1), CODETEKI_BRAND['light']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
        ]))
        scores_table.hAlign = 'CENTER'
        elements.append(scores_table)

        return elements

    def _format_score(self, score: Optional[float]) -> str:
        """Format score for display."""
        if score is None:
            return 'N/A'
        return f"{int(round(score))}"

    def _build_executive_summary(self) -> list:
        """Build the executive summary section."""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=CODETEKI_BRAND['primary']))
        elements.append(Spacer(1, 0.2*inch))

        # Overall health assessment
        avg_score = 0
        count = 0
        for score in [self.site_audit.avg_performance, self.site_audit.avg_seo,
                      self.site_audit.avg_accessibility, self.site_audit.avg_best_practices]:
            if score is not None:
                avg_score += score
                count += 1

        overall_score = avg_score / count if count > 0 else 0

        if overall_score >= 90:
            health_status = "Excellent"
            health_color = CODETEKI_BRAND['success']
            health_text = "Your website is performing exceptionally well across all metrics."
        elif overall_score >= 70:
            health_status = "Good"
            health_color = CODETEKI_BRAND['success']
            health_text = "Your website is performing well with some room for improvement."
        elif overall_score >= 50:
            health_status = "Needs Improvement"
            health_color = CODETEKI_BRAND['warning']
            health_text = "Your website has significant issues that should be addressed to improve performance and user experience."
        else:
            health_status = "Critical"
            health_color = CODETEKI_BRAND['danger']
            health_text = "Your website requires immediate attention. Critical issues are affecting performance and user experience."

        # Health status box
        health_data = [[
            Paragraph(f"<font size='14'><b>Overall Health:</b></font>", self.styles['ReportBody']),
            Paragraph(f"<font size='16' color='{health_color.hexval()}'><b>{health_status}</b></font>", self.styles['ReportBody']),
        ]]
        health_table = Table(health_data, colWidths=[2*inch, 4*inch])
        health_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), CODETEKI_BRAND['light']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(health_table)
        elements.append(Spacer(1, 0.15*inch))

        elements.append(Paragraph(health_text, self.styles['ReportBody']))
        elements.append(Spacer(1, 0.3*inch))

        # Key metrics summary
        elements.append(Paragraph("Key Findings", self.styles['SubsectionHeader']))

        findings = []

        # Performance finding
        if self.site_audit.avg_performance is not None:
            perf = self.site_audit.avg_performance
            if perf >= 90:
                findings.append(f"<b>Performance ({int(perf)}/100):</b> Excellent loading speeds and interactivity.")
            elif perf >= 50:
                findings.append(f"<b>Performance ({int(perf)}/100):</b> Room for improvement in loading speeds and interactivity.")
            else:
                findings.append(f"<b>Performance ({int(perf)}/100):</b> Critical - Poor loading speeds significantly impacting user experience.")

        # SEO finding
        if self.site_audit.avg_seo is not None:
            seo = self.site_audit.avg_seo
            if seo >= 90:
                findings.append(f"<b>SEO ({int(seo)}/100):</b> Excellent search engine optimization.")
            elif seo >= 50:
                findings.append(f"<b>SEO ({int(seo)}/100):</b> Some SEO improvements recommended.")
            else:
                findings.append(f"<b>SEO ({int(seo)}/100):</b> Critical SEO issues affecting search visibility.")

        # Issue summary
        if self.site_audit.critical_issues > 0:
            findings.append(f"<b>Critical Issues:</b> {self.site_audit.critical_issues} issues require immediate attention.")
        if self.site_audit.warning_issues > 0:
            findings.append(f"<b>Warnings:</b> {self.site_audit.warning_issues} warnings should be reviewed.")

        for finding in findings:
            elements.append(Paragraph(f"  {finding}", self.styles['ReportBody']))

        return elements

    def _build_score_dashboard(self) -> list:
        """Build the score dashboard section."""
        elements = []

        elements.append(Paragraph("Performance Scores", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=CODETEKI_BRAND['primary']))
        elements.append(Spacer(1, 0.3*inch))

        # Score cards
        scores = [
            ('Performance', self.site_audit.avg_performance, 'Page load speed, interactivity, and visual stability'),
            ('SEO', self.site_audit.avg_seo, 'Search engine optimization and discoverability'),
            ('Accessibility', self.site_audit.avg_accessibility, 'Usability for people with disabilities'),
            ('Best Practices', self.site_audit.avg_best_practices, 'Modern web development standards'),
        ]

        score_rows = []
        for name, score, description in scores:
            color = get_score_color(score)
            score_text = self._format_score(score)

            row = [
                Paragraph(f"<font size='12'><b>{name}</b></font>", self.styles['ReportBody']),
                Paragraph(f"<font size='20' color='{color.hexval()}'><b>{score_text}</b></font>", self.styles['ReportBody']),
                Paragraph(f"<font size='9' color='{CODETEKI_BRAND['gray'].hexval()}'>{description}</font>", self.styles['ReportBody']),
            ]
            score_rows.append(row)

        score_table = Table(score_rows, colWidths=[1.5*inch, 1*inch, 3.5*inch])
        score_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, CODETEKI_BRAND['border']),
        ]))
        elements.append(score_table)

        elements.append(Spacer(1, 0.3*inch))

        # Score interpretation guide
        elements.append(Paragraph("Score Interpretation", self.styles['SubsectionHeader']))

        guide_data = [
            [Paragraph(f"<font color='{CODETEKI_BRAND['success'].hexval()}'>90-100</font>", self.styles['ReportBody']), 'Good - No action needed'],
            [Paragraph(f"<font color='{CODETEKI_BRAND['warning'].hexval()}'>50-89</font>", self.styles['ReportBody']), 'Needs Improvement - Should be addressed'],
            [Paragraph(f"<font color='{CODETEKI_BRAND['danger'].hexval()}'>0-49</font>", self.styles['ReportBody']), 'Poor - Requires immediate attention'],
        ]

        guide_table = Table(guide_data, colWidths=[1*inch, 5*inch])
        guide_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(guide_table)

        return elements

    def _build_core_web_vitals(self) -> list:
        """Build the Core Web Vitals section."""
        from ..models import PageAudit

        elements = []

        elements.append(Paragraph("Core Web Vitals", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=CODETEKI_BRAND['primary']))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "Core Web Vitals are Google's essential metrics for user experience. These directly impact your search rankings.",
            self.styles['ReportBody']
        ))
        elements.append(Spacer(1, 0.2*inch))

        # Get page audits
        page_audits = self.site_audit.page_audits.all()[:10]

        if not page_audits:
            elements.append(Paragraph("No page audits available.", self.styles['ReportBody']))
            return elements

        # Calculate averages
        metrics = {'lcp': [], 'cls': [], 'tbt': [], 'fcp': [], 'si': [], 'ttfb': []}

        for page in page_audits:
            if page.lcp is not None:
                metrics['lcp'].append(page.lcp)
            if page.cls is not None:
                metrics['cls'].append(page.cls)
            if page.tbt is not None:
                metrics['tbt'].append(page.tbt)
            if page.fcp is not None:
                metrics['fcp'].append(page.fcp)
            if page.si is not None:
                metrics['si'].append(page.si)
            if page.ttfb is not None:
                metrics['ttfb'].append(page.ttfb)

        # CWV data
        cwv_data = [
            ('LCP', 'Largest Contentful Paint',
             sum(metrics['lcp'])/len(metrics['lcp']) if metrics['lcp'] else None, 's', 'lcp',
             'Measures loading performance. Should be under 2.5s.'),
            ('CLS', 'Cumulative Layout Shift',
             sum(metrics['cls'])/len(metrics['cls']) if metrics['cls'] else None, '', 'cls',
             'Measures visual stability. Should be under 0.1.'),
            ('TBT', 'Total Blocking Time',
             sum(metrics['tbt'])/len(metrics['tbt']) if metrics['tbt'] else None, 'ms', 'tbt',
             'Measures interactivity. Should be under 200ms.'),
            ('FCP', 'First Contentful Paint',
             sum(metrics['fcp'])/len(metrics['fcp']) if metrics['fcp'] else None, 's', 'fcp',
             'First content rendered. Should be under 1.8s.'),
            ('SI', 'Speed Index',
             sum(metrics['si'])/len(metrics['si']) if metrics['si'] else None, 's', 'si',
             'Visual progress speed. Should be under 3.4s.'),
        ]

        # Build CWV table
        cwv_rows = [['Metric', 'Value', 'Status', 'Description']]

        for abbr, name, value, unit, key, desc in cwv_data:
            if value is not None:
                color = get_cwv_color(key, value)
                if key == 'cls':
                    value_str = f"{value:.3f}"
                elif unit == 'ms':
                    value_str = f"{int(value)}{unit}"
                else:
                    value_str = f"{value:.2f}{unit}"

                status = 'Good' if color == CODETEKI_BRAND['success'] else ('Needs Work' if color == CODETEKI_BRAND['warning'] else 'Poor')

                cwv_rows.append([
                    Paragraph(f"<b>{abbr}</b><br/><font size='8'>{name}</font>", self.styles['ReportBody']),
                    Paragraph(f"<font size='14' color='{color.hexval()}'><b>{value_str}</b></font>", self.styles['ReportBody']),
                    Paragraph(f"<font color='{color.hexval()}'>{status}</font>", self.styles['ReportBody']),
                    Paragraph(f"<font size='8'>{desc}</font>", self.styles['ReportBody']),
                ])

        cwv_table = Table(cwv_rows, colWidths=[1.5*inch, 1*inch, 0.8*inch, 2.7*inch])
        cwv_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), CODETEKI_BRAND['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
        ]))
        elements.append(cwv_table)

        return elements

    def _build_issues_breakdown(self) -> list:
        """Build the issues breakdown section."""
        from ..models import AuditIssue

        elements = []

        elements.append(Paragraph("Issues Overview", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=CODETEKI_BRAND['primary']))
        elements.append(Spacer(1, 0.2*inch))

        # Get issue counts by category and severity
        issues = AuditIssue.objects.filter(
            page_audit__site_audit=self.site_audit
        ).exclude(severity='passed')

        # Count by severity
        severity_counts = {
            'error': issues.filter(severity='error').count(),
            'warning': issues.filter(severity='warning').count(),
            'info': issues.filter(severity='info').count(),
        }

        # Count by category
        category_counts = {
            'performance': issues.filter(category='performance').count(),
            'seo': issues.filter(category='seo').count(),
            'accessibility': issues.filter(category='accessibility').count(),
            'best-practices': issues.filter(category='best-practices').count(),
        }

        # Summary row
        elements.append(Paragraph("Issues by Severity", self.styles['SubsectionHeader']))

        severity_data = [[
            Paragraph(f"<font color='{CODETEKI_BRAND['danger'].hexval()}'><b>Errors</b></font>", self.styles['ReportBody']),
            Paragraph(f"<font color='{CODETEKI_BRAND['warning'].hexval()}'><b>Warnings</b></font>", self.styles['ReportBody']),
            Paragraph(f"<font color='{CODETEKI_BRAND['info'].hexval()}'><b>Info</b></font>", self.styles['ReportBody']),
        ], [
            Paragraph(f"<font size='18' color='{CODETEKI_BRAND['danger'].hexval()}'><b>{severity_counts['error']}</b></font>", self.styles['ReportBody']),
            Paragraph(f"<font size='18' color='{CODETEKI_BRAND['warning'].hexval()}'><b>{severity_counts['warning']}</b></font>", self.styles['ReportBody']),
            Paragraph(f"<font size='18' color='{CODETEKI_BRAND['info'].hexval()}'><b>{severity_counts['info']}</b></font>", self.styles['ReportBody']),
        ]]

        severity_table = Table(severity_data, colWidths=[2*inch, 2*inch, 2*inch])
        severity_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), CODETEKI_BRAND['light']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(severity_table)
        elements.append(Spacer(1, 0.3*inch))

        # Issues by category
        elements.append(Paragraph("Issues by Category", self.styles['SubsectionHeader']))

        category_rows = [['Category', 'Issues', 'Description']]
        category_info = [
            ('Performance', category_counts['performance'], 'Speed, loading, and responsiveness issues'),
            ('SEO', category_counts['seo'], 'Search engine optimization issues'),
            ('Accessibility', category_counts['accessibility'], 'Issues affecting users with disabilities'),
            ('Best Practices', category_counts['best-practices'], 'Modern web standards and security'),
        ]

        for name, count, desc in category_info:
            category_rows.append([name, str(count), desc])

        category_table = Table(category_rows, colWidths=[1.5*inch, 1*inch, 3.5*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), CODETEKI_BRAND['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
        ]))
        elements.append(category_table)

        return elements

    def _build_issues_by_url(self) -> list:
        """Build detailed issues grouped by URL."""
        from ..models import AuditIssue, PageAudit

        elements = []

        elements.append(Paragraph("Detailed Issues by Page", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=CODETEKI_BRAND['primary']))
        elements.append(Spacer(1, 0.2*inch))

        # Get page audits with issues
        page_audits = self.site_audit.page_audits.prefetch_related('issues').all()

        for page in page_audits[:10]:  # Limit to 10 pages
            issues = page.issues.exclude(severity='passed').order_by('severity', '-savings_ms')[:15]

            if not issues:
                continue

            # Page header
            url_display = page.url
            if len(url_display) > 60:
                url_display = url_display[:57] + '...'

            elements.append(Paragraph(
                f"<font color='{CODETEKI_BRAND['primary'].hexval()}'><b>{url_display}</b></font>",
                self.styles['SubsectionHeader']
            ))

            # Page scores
            score_text = f"Performance: {page.performance_score or 'N/A'} | SEO: {page.seo_score or 'N/A'} | Accessibility: {page.accessibility_score or 'N/A'}"
            elements.append(Paragraph(
                f"<font size='9' color='{CODETEKI_BRAND['gray'].hexval()}'>{score_text}</font>",
                self.styles['ReportBody']
            ))
            elements.append(Spacer(1, 0.1*inch))

            # Issues table
            issue_rows = [['Severity', 'Issue', 'Impact', 'Date Found']]

            for issue in issues:
                severity_color = {
                    'error': CODETEKI_BRAND['danger'],
                    'warning': CODETEKI_BRAND['warning'],
                    'info': CODETEKI_BRAND['info'],
                }.get(issue.severity, CODETEKI_BRAND['gray'])

                # Get the date - use created_at or updated_at
                issue_date = issue.created_at.strftime('%Y-%m-%d') if issue.created_at else 'N/A'

                savings = ''
                if issue.savings_ms > 0:
                    savings = f"{int(issue.savings_ms)}ms"
                elif issue.savings_bytes > 0:
                    savings = f"{issue.savings_bytes // 1024}KB"

                issue_rows.append([
                    Paragraph(f"<font color='{severity_color.hexval()}'><b>{issue.severity.upper()}</b></font>", self.styles['ReportBody']),
                    Paragraph(f"<font size='9'>{issue.title[:50]}{'...' if len(issue.title) > 50 else ''}</font>", self.styles['ReportBody']),
                    savings or '-',
                    issue_date,
                ])

            issue_table = Table(issue_rows, colWidths=[0.8*inch, 3*inch, 0.8*inch, 0.9*inch])
            issue_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), CODETEKI_BRAND['light']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (0, -1), 'CENTER'),
                ('ALIGN', (2, 0), (3, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
                ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
            ]))
            elements.append(issue_table)
            elements.append(Spacer(1, 0.2*inch))

        return elements

    def _build_ai_analysis(self) -> list:
        """Build the AI analysis section."""
        elements = []

        elements.append(Paragraph("AI-Powered Analysis & Recommendations", self.styles['SectionHeader']))
        elements.append(HRFlowable(width="100%", thickness=2, color=CODETEKI_BRAND['primary']))
        elements.append(Spacer(1, 0.2*inch))

        elements.append(Paragraph(
            "The following analysis was generated by AI based on your audit results:",
            self.styles['ReportBody']
        ))
        elements.append(Spacer(1, 0.15*inch))

        # Parse and format the AI analysis
        ai_text = self.site_audit.ai_analysis or ""

        # Split by lines and format
        lines = ai_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                elements.append(Spacer(1, 0.05*inch))
                continue

            # Handle markdown-style headers
            if line.startswith('### '):
                elements.append(Paragraph(line[4:], self.styles['SubsectionHeader']))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], self.styles['SubsectionHeader']))
            elif line.startswith('# '):
                elements.append(Paragraph(line[2:], self.styles['SectionHeader']))
            elif line.startswith('- ') or line.startswith('* '):
                elements.append(Paragraph(f"  {line}", self.styles['ReportBody']))
            elif line.startswith('```'):
                # Skip code block markers
                continue
            else:
                # Handle bold text
                import re
                line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)
                line = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', line)
                elements.append(Paragraph(line, self.styles['ReportBody']))

        return elements


def generate_seo_audit_pdf(site_audit) -> bytes:
    """
    Convenience function to generate a PDF report.

    Args:
        site_audit: SiteAudit model instance

    Returns:
        PDF content as bytes
    """
    generator = SEOReportPDFGenerator(site_audit)
    return generator.generate()
