"""
SEO Audit PDF Report Generator - Premium Version.

Professional PDF report generation with Codeteki branding.
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
    PageBreak, Image, HRFlowable, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Wedge
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.widgets.markers import makeMarker

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
    'gray_light': colors.HexColor('#9CA3AF'),    # Gray 400
    'border': colors.HexColor('#E5E7EB'),        # Gray 200
    'orange': colors.HexColor('#F97316'),        # Orange
    'pink': colors.HexColor('#EC4899'),          # Pink
}


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


def get_cwv_status(metric: str, value: Optional[float]) -> tuple:
    """Get status and color based on Core Web Vitals thresholds."""
    if value is None:
        return 'N/A', CODETEKI_BRAND['gray']

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
        return 'N/A', CODETEKI_BRAND['gray']

    good, poor = thresholds[metric]
    if value <= good:
        return 'Good', CODETEKI_BRAND['success']
    elif value <= poor:
        return 'Needs Work', CODETEKI_BRAND['warning']
    else:
        return 'Poor', CODETEKI_BRAND['danger']


class SEOReportPDFGenerator:
    """
    Premium PDF Report Generator for SEO Audits.
    Designed to match/exceed SEMrush report quality.
    """

    def __init__(self, site_audit):
        self.site_audit = site_audit
        self.buffer = io.BytesIO()
        self.styles = self._create_styles()
        self.logo_path = self._get_logo_path()
        self.width = A4[0] - 1.5*inch  # Available width

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

        # Main Title
        styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=CODETEKI_BRAND['dark'],
            spaceAfter=5,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
        ))

        # Domain highlight
        styles.add(ParagraphStyle(
            name='DomainTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=CODETEKI_BRAND['primary'],
            spaceAfter=10,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
        ))

        # Summary text
        styles.add(ParagraphStyle(
            name='SummaryText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=CODETEKI_BRAND['dark'],
            spaceAfter=20,
            leading=16,
        ))

        # Section header
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=18,
            textColor=CODETEKI_BRAND['dark'],
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold',
        ))

        # Section description
        styles.add(ParagraphStyle(
            name='SectionDesc',
            parent=styles['Normal'],
            fontSize=10,
            textColor=CODETEKI_BRAND['gray'],
            spaceAfter=15,
            leading=14,
        ))

        # Subsection header
        styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=CODETEKI_BRAND['dark'],
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold',
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='ReportBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor=CODETEKI_BRAND['dark'],
            spaceAfter=6,
            leading=14,
        ))

        # Small text
        styles.add(ParagraphStyle(
            name='SmallText',
            parent=styles['Normal'],
            fontSize=8,
            textColor=CODETEKI_BRAND['gray'],
            leading=10,
        ))

        # URL text
        styles.add(ParagraphStyle(
            name='URLText',
            parent=styles['Normal'],
            fontSize=9,
            textColor=CODETEKI_BRAND['primary'],
            fontName='Helvetica',
        ))

        # Metric badge
        styles.add(ParagraphStyle(
            name='MetricBadge',
            parent=styles['Normal'],
            fontSize=9,
            textColor=CODETEKI_BRAND['gray'],
            backColor=CODETEKI_BRAND['light'],
        ))

        return styles

    def _create_score_donut(self, score: float, size: int = 100) -> Drawing:
        """Create a donut chart showing the score."""
        d = Drawing(size, size)

        # Background circle (gray)
        d.add(Wedge(size/2, size/2, size/2 - 5, 0, 360,
                    fillColor=CODETEKI_BRAND['border'], strokeColor=None))

        # Score arc
        if score > 0:
            angle = (score / 100) * 360
            color = get_score_color(score)
            d.add(Wedge(size/2, size/2, size/2 - 5, 90, 90 - angle,
                        fillColor=color, strokeColor=None))

        # Inner circle (white, creates donut effect)
        d.add(Wedge(size/2, size/2, size/2 - 20, 0, 360,
                    fillColor=colors.white, strokeColor=None))

        # Score text
        d.add(String(size/2, size/2 + 5, str(int(score)),
                     fontSize=20, fillColor=CODETEKI_BRAND['dark'],
                     textAnchor='middle', fontName='Helvetica-Bold'))
        d.add(String(size/2, size/2 - 12, 'SEO Score',
                     fontSize=8, fillColor=CODETEKI_BRAND['gray'],
                     textAnchor='middle'))

        return d

    def _create_progress_bar(self, percentage: float, width: float = 150, height: float = 12,
                             color: colors.Color = None) -> Drawing:
        """Create a progress bar."""
        d = Drawing(width, height)

        # Background
        d.add(Rect(0, 0, width, height, fillColor=CODETEKI_BRAND['border'],
                   strokeColor=None, rx=3, ry=3))

        # Progress
        if percentage > 0:
            bar_color = color or get_score_color(percentage)
            bar_width = (percentage / 100) * width
            d.add(Rect(0, 0, bar_width, height, fillColor=bar_color,
                       strokeColor=None, rx=3, ry=3))

        return d

    def _get_priority_symbol(self, severity: str) -> str:
        """Get priority symbol based on severity."""
        symbols = {
            'error': '🚩',      # Red flag
            'warning': '⚠️',    # Warning
            'info': 'ℹ️',       # Info
            'passed': '✅',     # Check
        }
        return symbols.get(severity, '•')

    def generate(self) -> bytes:
        """Generate the complete PDF report."""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch,
        )

        elements = []

        # Header/Title Section
        elements.extend(self._build_header())

        # Overview Section with Score Chart
        elements.extend(self._build_overview())

        # Issues and Recommendations
        elements.append(PageBreak())
        elements.extend(self._build_issues_recommendations())

        # Page Speed & Core Web Vitals
        elements.append(PageBreak())
        elements.extend(self._build_page_speed_section())

        # Audited Pages List
        elements.append(PageBreak())
        elements.extend(self._build_audited_pages())

        # AI Analysis (if available)
        if self.site_audit.ai_analysis:
            elements.append(PageBreak())
            elements.extend(self._build_ai_analysis())

        # Build PDF
        doc.build(elements, onFirstPage=self._add_footer, onLaterPages=self._add_footer)

        pdf_content = self.buffer.getvalue()
        self.buffer.close()
        return pdf_content

    def _add_footer(self, canvas, doc):
        """Add footer to each page."""
        canvas.saveState()

        # Footer line
        canvas.setStrokeColor(CODETEKI_BRAND['border'])
        canvas.setLineWidth(0.5)
        canvas.line(0.75*inch, 0.5*inch, A4[0] - 0.75*inch, 0.5*inch)

        # Footer text
        footer_text = f"Codeteki SEO Audit Report | Generated: {datetime.now().strftime('%B %d, %Y')}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(CODETEKI_BRAND['gray'])
        canvas.drawString(0.75*inch, 0.35*inch, footer_text)

        # Page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(A4[0] - 0.75*inch, 0.35*inch, f"Page {page_num}")

        canvas.restoreState()

    def _build_header(self) -> list:
        """Build the header section."""
        elements = []

        # Logo (if available)
        if self.logo_path:
            try:
                logo = Image(self.logo_path, width=1.5*inch, height=0.45*inch)
                elements.append(logo)
                elements.append(Spacer(1, 0.2*inch))
            except Exception as e:
                logger.warning(f"Could not load logo: {e}")

        # Title
        elements.append(Paragraph(
            f"SEO Audit Results for <font color='{CODETEKI_BRAND['primary'].hexval()}'>{self.site_audit.domain}</font>",
            self.styles['ReportTitle']
        ))

        # Summary line
        avg_seo = self.site_audit.avg_seo or 0
        critical = self.site_audit.critical_issues or 0
        warnings = self.site_audit.warning_issues or 0
        total_pages = self.site_audit.total_pages or 0

        summary = (
            f"The SEO score for this website is <b>{int(avg_seo)} out of 100</b>. "
            f"We found <b><font color='{CODETEKI_BRAND['danger'].hexval()}'>{critical} critical issues</font></b> "
            f"and <b><font color='{CODETEKI_BRAND['warning'].hexval()}'>{warnings} warnings</font></b> "
            f"across <b>{total_pages} pages</b> that should be addressed to improve Google rankings and drive more traffic."
        )
        elements.append(Paragraph(summary, self.styles['SummaryText']))

        return elements

    def _build_overview(self) -> list:
        """Build the overview section with score chart."""
        elements = []

        elements.append(Paragraph("Overview", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "This section summarizes your site's overall SEO performance, providing insights from performance, "
            "SEO, accessibility, and best practices audits, highlighting both strengths and priority issues.",
            self.styles['SectionDesc']
        ))

        # Calculate overall score
        scores = [
            self.site_audit.avg_performance,
            self.site_audit.avg_seo,
            self.site_audit.avg_accessibility,
            self.site_audit.avg_best_practices
        ]
        valid_scores = [s for s in scores if s is not None]
        overall_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        # Create score breakdown data
        score_data = [
            ('Performance', self.site_audit.avg_performance or 0, CODETEKI_BRAND['orange']),
            ('SEO', self.site_audit.avg_seo or 0, CODETEKI_BRAND['warning']),
            ('Accessibility', self.site_audit.avg_accessibility or 0, CODETEKI_BRAND['success']),
            ('Best Practices', self.site_audit.avg_best_practices or 0, CODETEKI_BRAND['info']),
        ]

        # Build score table with donut and bars
        donut = self._create_score_donut(overall_score, 100)

        # Score bars
        bar_rows = []
        for name, score, color in score_data:
            bar = self._create_progress_bar(score, 180, 10, color)
            bar_rows.append([
                Paragraph(name, self.styles['ReportBody']),
                bar,
                Paragraph(f"<b>{int(score)}%</b>", self.styles['ReportBody']),
            ])

        bar_table = Table(bar_rows, colWidths=[1.2*inch, 2.8*inch, 0.5*inch])
        bar_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))

        # Combine donut and bars
        main_table = Table([[donut, Spacer(0.3*inch, 0), bar_table]],
                          colWidths=[1.2*inch, 0.3*inch, 4.5*inch])
        main_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, -1), CODETEKI_BRAND['light']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(main_table)

        elements.append(Spacer(1, 0.2*inch))

        # Quick stats
        stats_data = [[
            Paragraph(f"<font size='16'><b>{self.site_audit.total_pages}</b></font><br/><font size='8' color='{CODETEKI_BRAND['gray'].hexval()}'>Pages Audited</font>", self.styles['ReportBody']),
            Paragraph(f"<font size='16'><b>{self.site_audit.total_issues}</b></font><br/><font size='8' color='{CODETEKI_BRAND['gray'].hexval()}'>Total Issues</font>", self.styles['ReportBody']),
            Paragraph(f"<font size='16' color='{CODETEKI_BRAND['danger'].hexval()}'><b>{self.site_audit.critical_issues}</b></font><br/><font size='8' color='{CODETEKI_BRAND['gray'].hexval()}'>Critical</font>", self.styles['ReportBody']),
            Paragraph(f"<font size='16' color='{CODETEKI_BRAND['warning'].hexval()}'><b>{self.site_audit.warning_issues}</b></font><br/><font size='8' color='{CODETEKI_BRAND['gray'].hexval()}'>Warnings</font>", self.styles['ReportBody']),
        ]]

        stats_table = Table(stats_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        stats_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        elements.append(stats_table)

        return elements

    def _build_issues_recommendations(self) -> list:
        """Build the issues and recommendations section."""
        from ..models import AuditIssue

        elements = []

        elements.append(Paragraph("Issues and Recommendations", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "This section identifies your site's most critical SEO issues and delivers clear recommendations "
            "to resolve them and strengthen search performance.",
            self.styles['SectionDesc']
        ))

        # Get all issues
        issues = AuditIssue.objects.filter(
            page_audit__site_audit=self.site_audit
        ).exclude(severity='passed').select_related('page_audit').order_by('severity', '-savings_ms')[:25]

        if not issues:
            elements.append(Paragraph("No issues found. Great job!", self.styles['ReportBody']))
            return elements

        # Table header
        header = ['Type', 'Element', 'Priority', 'Problem and Recommendation']
        rows = [header]

        for issue in issues:
            # Determine priority icon/color
            if issue.severity == 'error':
                priority = Paragraph(f"<font color='{CODETEKI_BRAND['danger'].hexval()}'>●</font>", self.styles['ReportBody'])
            elif issue.severity == 'warning':
                priority = Paragraph(f"<font color='{CODETEKI_BRAND['warning'].hexval()}'>●</font>", self.styles['ReportBody'])
            else:
                priority = Paragraph(f"<font color='{CODETEKI_BRAND['info'].hexval()}'>●</font>", self.styles['ReportBody'])

            # Truncate title if needed
            title = issue.title[:40] + '...' if len(issue.title) > 40 else issue.title

            # Create recommendation text
            desc = issue.description[:150] + '...' if len(issue.description) > 150 else issue.description

            rows.append([
                Paragraph(f"<font size='8'>{issue.category.title()}</font>", self.styles['ReportBody']),
                Paragraph(f"<font size='9'><b>{title}</b></font>", self.styles['ReportBody']),
                priority,
                Paragraph(f"<font size='8'>{desc}</font>", self.styles['SmallText']),
            ])

        issue_table = Table(rows, colWidths=[0.9*inch, 1.3*inch, 0.5*inch, 3.3*inch])
        issue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), CODETEKI_BRAND['light']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('TEXTCOLOR', (0, 0), (-1, 0), CODETEKI_BRAND['gray']),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
        ]))
        elements.append(issue_table)

        return elements

    def _build_page_speed_section(self) -> list:
        """Build the Page Speed & Core Web Vitals section."""
        elements = []

        elements.append(Paragraph("Page Speed & Core Web Vitals", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "This section shows your page load time, Core Web Vitals, and other speed signals that affect "
            "search results and user experience. All recommendations follow Google's performance guidelines.",
            self.styles['SectionDesc']
        ))

        # Get page audits
        page_audits = self.site_audit.page_audits.all()[:10]

        if not page_audits:
            elements.append(Paragraph("No page speed data available.", self.styles['ReportBody']))
            return elements

        # Calculate averages
        metrics_data = {
            'lcp': [], 'cls': [], 'tbt': [], 'fcp': [], 'si': [], 'ttfb': [], 'inp': []
        }
        perf_scores = []

        for page in page_audits:
            if page.performance_score:
                perf_scores.append(page.performance_score)
            if page.lcp:
                metrics_data['lcp'].append(page.lcp)
            if page.cls:
                metrics_data['cls'].append(page.cls)
            if page.tbt:
                metrics_data['tbt'].append(page.tbt)
            if page.fcp:
                metrics_data['fcp'].append(page.fcp)
            if page.si:
                metrics_data['si'].append(page.si)
            if page.ttfb:
                metrics_data['ttfb'].append(page.ttfb)
            if page.inp:
                metrics_data['inp'].append(page.inp)

        # Performance Score
        avg_perf = sum(perf_scores) / len(perf_scores) if perf_scores else 0
        perf_status, perf_color = ('Good', CODETEKI_BRAND['success']) if avg_perf >= 90 else (('Needs Work', CODETEKI_BRAND['warning']) if avg_perf >= 50 else ('Poor', CODETEKI_BRAND['danger']))

        cwv_items = [
            ('Performance Score', None, f"{int(avg_perf)}/100", perf_status, perf_color,
             "Your page performs reasonably well. Compress images, remove unused CSS/JavaScript to improve."),
        ]

        # Core Web Vitals
        cwv_definitions = [
            ('Largest Contentful Paint (LCP)', 'lcp', 's',
             "The main image or block of text appears quickly, giving users confidence the page is loading."),
            ('Cumulative Layout Shift (CLS)', 'cls', '',
             "Page elements are visually stable while loading, so elements don't jump around."),
            ('Total Blocking Time (TBT)', 'tbt', 'ms',
             "Scripts rarely block the main thread, so interactions feel smooth and responsive."),
            ('First Contentful Paint (FCP)', 'fcp', 's',
             "The first text or image appears quickly, giving users feedback that the page is loading."),
            ('Speed Index', 'si', 's',
             "Visual content loads progressively. Compress images and defer non-critical scripts."),
            ('Time to First Byte (TTFB)', 'ttfb', 'ms',
             "The server responds quickly, so users start receiving data almost instantly."),
        ]

        for name, key, unit, desc in cwv_definitions:
            values = metrics_data.get(key, [])
            if values:
                avg_val = sum(values) / len(values)
                status, color = get_cwv_status(key, avg_val)
                if key == 'cls':
                    display_val = f"{avg_val:.3f}"
                elif unit == 'ms':
                    display_val = f"{int(avg_val)}ms"
                else:
                    display_val = f"{avg_val:.2f}s"
                cwv_items.append((name, key, display_val, status, color, desc))

        # Build CWV table
        rows = []
        for name, key, value, status, color, desc in cwv_items:
            # Status indicator
            if status == 'Good':
                indicator = Paragraph(f"<font color='{CODETEKI_BRAND['success'].hexval()}'>✓</font>", self.styles['ReportBody'])
            elif status == 'Needs Work':
                indicator = Paragraph(f"<font color='{CODETEKI_BRAND['warning'].hexval()}'>⚠</font>", self.styles['ReportBody'])
            else:
                indicator = Paragraph(f"<font color='{CODETEKI_BRAND['danger'].hexval()}'>✗</font>", self.styles['ReportBody'])

            # Value badge
            value_badge = Paragraph(
                f"<font size='8' backcolor='{CODETEKI_BRAND['light'].hexval()}'> {value} </font>",
                self.styles['ReportBody']
            )

            rows.append([
                Paragraph(f"<b>{name}</b>", self.styles['ReportBody']),
                indicator,
                Paragraph(f"<font size='9'>{desc}</font><br/>{value_badge}", self.styles['SmallText']),
            ])

        cwv_table = Table(rows, colWidths=[1.8*inch, 0.4*inch, 3.8*inch])
        cwv_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
        ]))
        elements.append(cwv_table)

        return elements

    def _build_audited_pages(self) -> list:
        """Build the list of all audited pages with their scores."""
        elements = []

        elements.append(Paragraph("Audited Pages", self.styles['SectionHeader']))
        elements.append(Paragraph(
            f"This section lists all {self.site_audit.total_pages} pages that were audited, "
            "showing individual performance scores for each URL.",
            self.styles['SectionDesc']
        ))

        page_audits = self.site_audit.page_audits.all()

        if not page_audits:
            elements.append(Paragraph("No pages audited.", self.styles['ReportBody']))
            return elements

        # Table header
        header = ['URL', 'Performance', 'SEO', 'Accessibility', 'Best Practices']
        rows = [header]

        for page in page_audits:
            # Truncate URL
            url = page.url
            if len(url) > 40:
                url = url[:37] + '...'

            # Color-code scores
            def score_cell(score):
                if score is None:
                    return 'N/A'
                color = get_score_color(score)
                return Paragraph(f"<font color='{color.hexval()}'><b>{int(score)}</b></font>", self.styles['ReportBody'])

            rows.append([
                Paragraph(f"<font size='8' color='{CODETEKI_BRAND['primary'].hexval()}'>{url}</font>", self.styles['ReportBody']),
                score_cell(page.performance_score),
                score_cell(page.seo_score),
                score_cell(page.accessibility_score),
                score_cell(page.best_practices_score),
            ])

        page_table = Table(rows, colWidths=[2.5*inch, 0.8*inch, 0.6*inch, 0.9*inch, 1*inch])
        page_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), CODETEKI_BRAND['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, CODETEKI_BRAND['border']),
            ('BOX', (0, 0), (-1, -1), 1, CODETEKI_BRAND['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, CODETEKI_BRAND['light']]),
        ]))
        elements.append(page_table)

        return elements

    def _build_ai_analysis(self) -> list:
        """Build the AI analysis section."""
        elements = []

        elements.append(Paragraph("AI-Powered Analysis & Recommendations", self.styles['SectionHeader']))
        elements.append(Paragraph(
            "The following analysis was generated by AI based on your audit results, providing "
            "prioritized recommendations and implementation guidance.",
            self.styles['SectionDesc']
        ))

        # Parse and format the AI analysis
        ai_text = self.site_audit.ai_analysis or ""
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
                elements.append(Paragraph(f"• {line[2:]}", self.styles['ReportBody']))
            elif line.startswith('```'):
                continue
            else:
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
