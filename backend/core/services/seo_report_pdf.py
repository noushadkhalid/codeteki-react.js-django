"""
SEO Audit PDF Report Generator - Premium Edition.

Professional PDF report generation with Codeteki branding.
Designed to match/exceed SEMrush, Ahrefs, and Moz report quality.
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
    PageBreak, Image, HRFlowable, KeepTogether, ListFlowable, ListItem,
    CondPageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Wedge, Line
from reportlab.graphics.charts.piecharts import Pie

logger = logging.getLogger(__name__)

# Premium Brand Colors
BRAND = {
    'primary': colors.HexColor('#6366F1'),       # Indigo
    'primary_dark': colors.HexColor('#4338CA'),  # Darker Indigo
    'secondary': colors.HexColor('#8B5CF6'),     # Purple
    'accent': colors.HexColor('#06B6D4'),        # Cyan
    'success': colors.HexColor('#10B981'),       # Emerald
    'warning': colors.HexColor('#F59E0B'),       # Amber
    'danger': colors.HexColor('#EF4444'),        # Red
    'info': colors.HexColor('#3B82F6'),          # Blue
    'dark': colors.HexColor('#111827'),          # Gray 900
    'text': colors.HexColor('#1F2937'),          # Gray 800
    'text_secondary': colors.HexColor('#6B7280'), # Gray 500
    'light': colors.HexColor('#F9FAFB'),         # Gray 50
    'lighter': colors.HexColor('#F3F4F6'),       # Gray 100
    'border': colors.HexColor('#E5E7EB'),        # Gray 200
    'white': colors.white,
    'gradient_start': colors.HexColor('#4F46E5'),
    'gradient_end': colors.HexColor('#7C3AED'),
}


def get_score_color(score: Optional[float]) -> colors.Color:
    """Get color based on score (0-100)."""
    if score is None:
        return BRAND['text_secondary']
    score = float(score)
    if score >= 90:
        return BRAND['success']
    elif score >= 50:
        return BRAND['warning']
    else:
        return BRAND['danger']


def get_score_label(score: Optional[float]) -> str:
    """Get label based on score."""
    if score is None:
        return 'N/A'
    score = float(score)
    if score >= 90:
        return 'Good'
    elif score >= 50:
        return 'Needs Work'
    else:
        return 'Poor'


def get_cwv_status(metric: str, value: Optional[float]) -> tuple:
    """Get status and color based on Core Web Vitals thresholds."""
    if value is None:
        return 'N/A', BRAND['text_secondary'], 'No data available'

    thresholds = {
        'lcp': (2.5, 4.0, 's', 'Should be under 2.5s'),
        'fcp': (1.8, 3.0, 's', 'Should be under 1.8s'),
        'cls': (0.1, 0.25, '', 'Should be under 0.1'),
        'tbt': (200, 600, 'ms', 'Should be under 200ms'),
        'fid': (100, 300, 'ms', 'Should be under 100ms'),
        'inp': (200, 500, 'ms', 'Should be under 200ms'),
        'ttfb': (800, 1800, 'ms', 'Should be under 800ms'),
        'si': (3.4, 5.8, 's', 'Should be under 3.4s'),
    }

    if metric not in thresholds:
        return 'N/A', BRAND['text_secondary'], 'Unknown metric'

    good, poor, unit, desc = thresholds[metric]
    if value <= good:
        return 'Good', BRAND['success'], desc
    elif value <= poor:
        return 'Needs Work', BRAND['warning'], desc
    else:
        return 'Poor', BRAND['danger'], desc


class PremiumSEOReportGenerator:
    """
    Premium PDF Report Generator for SEO Audits.
    Designed to match/exceed SEMrush, Ahrefs, Moz report quality.
    """

    def __init__(self, site_audit):
        self.site_audit = site_audit
        self.buffer = io.BytesIO()
        self.styles = self._create_styles()
        self.logo_path = self._get_logo_path()
        self.page_width = A4[0]
        self.page_height = A4[1]
        self.content_width = A4[0] - 1.2*inch  # Available content width

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
        """Create premium custom styles."""
        styles = getSampleStyleSheet()

        # Cover Title
        styles.add(ParagraphStyle(
            name='CoverTitle',
            fontSize=36,
            textColor=BRAND['primary'],
            spaceAfter=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            leading=42,
        ))

        # Cover Subtitle
        styles.add(ParagraphStyle(
            name='CoverSubtitle',
            fontSize=18,
            textColor=BRAND['text'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica',
        ))

        # Section Title (large)
        styles.add(ParagraphStyle(
            name='SectionTitle',
            fontSize=22,
            textColor=BRAND['primary'],
            spaceBefore=20,
            spaceAfter=10,
            fontName='Helvetica-Bold',
        ))

        # Section Subtitle
        styles.add(ParagraphStyle(
            name='SectionSubtitle',
            fontSize=11,
            textColor=BRAND['text_secondary'],
            spaceAfter=15,
            leading=15,
        ))

        # Subsection Title
        styles.add(ParagraphStyle(
            name='SubsectionTitle',
            fontSize=14,
            textColor=BRAND['text'],
            spaceBefore=15,
            spaceAfter=8,
            fontName='Helvetica-Bold',
        ))

        # Body text
        styles.add(ParagraphStyle(
            name='Body',
            fontSize=10,
            textColor=BRAND['text'],
            spaceAfter=6,
            leading=14,
        ))

        # Small text
        styles.add(ParagraphStyle(
            name='Small',
            fontSize=9,
            textColor=BRAND['text_secondary'],
            leading=12,
        ))

        # Metric Value (large number)
        styles.add(ParagraphStyle(
            name='MetricValue',
            fontSize=28,
            textColor=BRAND['text'],
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
        ))

        # Metric Label
        styles.add(ParagraphStyle(
            name='MetricLabel',
            fontSize=9,
            textColor=BRAND['text_secondary'],
            alignment=TA_CENTER,
        ))

        # URL Style
        styles.add(ParagraphStyle(
            name='URL',
            fontSize=9,
            textColor=BRAND['primary'],
        ))

        # Table Header
        styles.add(ParagraphStyle(
            name='TableHeader',
            fontSize=9,
            textColor=BRAND['white'],
            fontName='Helvetica-Bold',
        ))

        # Table Cell
        styles.add(ParagraphStyle(
            name='TableCell',
            fontSize=9,
            textColor=BRAND['text'],
        ))

        return styles

    def _create_circular_score(self, score: float, size: int = 80, label: str = "Score") -> Drawing:
        """Create a circular score gauge."""
        d = Drawing(size + 20, size + 25)

        # Handle None score
        score = score if score is not None else 0
        score = float(score)

        center_x = (size + 20) / 2
        center_y = (size + 25) / 2 + 5
        radius = size / 2 - 5

        # Background circle
        d.add(Wedge(center_x, center_y, radius, 0, 360,
                    fillColor=BRAND['border'], strokeColor=None))

        # Score arc
        if score > 0:
            angle = (score / 100) * 360
            color = get_score_color(score)
            # Draw from top (90 degrees) going clockwise
            d.add(Wedge(center_x, center_y, radius, 90 - angle, 90,
                        fillColor=color, strokeColor=None))

        # Inner white circle (donut effect)
        inner_radius = radius - 12
        d.add(Wedge(center_x, center_y, inner_radius, 0, 360,
                    fillColor=BRAND['white'], strokeColor=None))

        # Score number
        d.add(String(center_x, center_y - 3, str(int(score)),
                     fontSize=18, fillColor=BRAND['text'],
                     textAnchor='middle', fontName='Helvetica-Bold'))

        # Label below
        d.add(String(center_x, 5, label,
                     fontSize=8, fillColor=BRAND['text_secondary'],
                     textAnchor='middle'))

        return d

    def _create_horizontal_bar(self, percentage: float, width: float = 180,
                                height: float = 8, label: str = "",
                                show_percent: bool = True) -> list:
        """Create a horizontal progress bar with label."""
        percentage = percentage if percentage is not None else 0
        percentage = float(percentage)

        d = Drawing(width, height)

        # Background bar
        d.add(Rect(0, 0, width, height,
                   fillColor=BRAND['lighter'], strokeColor=None,
                   rx=4, ry=4))

        # Progress bar
        if percentage > 0:
            bar_width = min((percentage / 100) * width, width)
            color = get_score_color(percentage)
            d.add(Rect(0, 0, bar_width, height,
                       fillColor=color, strokeColor=None,
                       rx=4, ry=4))

        return d

    def generate(self) -> bytes:
        """Generate the complete PDF report."""
        doc = SimpleDocTemplate(
            self.buffer,
            pagesize=A4,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch,
        )

        elements = []

        # 1. Cover Page
        elements.extend(self._build_cover_page())

        # 2. Executive Summary (same page as scores overview)
        elements.append(PageBreak())
        elements.extend(self._build_executive_summary())

        # 3. Core Web Vitals
        elements.append(CondPageBreak(4*inch))
        elements.extend(self._build_core_web_vitals())

        # 4. Issues Overview
        elements.append(PageBreak())
        elements.extend(self._build_issues_section())

        # 5. Audited Pages
        elements.append(CondPageBreak(3*inch))
        elements.extend(self._build_audited_pages())

        # 6. AI Analysis (if available)
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
        canvas.setStrokeColor(BRAND['border'])
        canvas.setLineWidth(0.5)
        canvas.line(0.6*inch, 0.4*inch, A4[0] - 0.6*inch, 0.4*inch)

        # Footer text
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(BRAND['text_secondary'])
        canvas.drawString(0.6*inch, 0.25*inch,
                         f"Codeteki SEO Audit Report | Generated: {datetime.now().strftime('%B %d, %Y')}")

        # Page number
        page_num = canvas.getPageNumber()
        canvas.drawRightString(A4[0] - 0.6*inch, 0.25*inch, f"Page {page_num}")

        canvas.restoreState()

    def _build_cover_page(self) -> list:
        """Build the premium cover page."""
        elements = []

        # Add some top spacing
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
        elements.append(Paragraph("SEO AUDIT REPORT", self.styles['CoverTitle']))
        elements.append(Spacer(1, 0.1*inch))

        # Domain
        elements.append(Paragraph(
            f"<font color='{BRAND['primary'].hexval()}'>{self.site_audit.domain}</font>",
            self.styles['CoverSubtitle']
        ))

        elements.append(Spacer(1, 0.8*inch))

        # Report info box
        info_data = [
            ['Report Name:', self.site_audit.name or f'{self.site_audit.domain} SEO Audit'],
            ['Strategy:', (self.site_audit.strategy or 'mobile').title()],
            ['Audit Date:', self.site_audit.created_at.strftime('%B %d, %Y') if self.site_audit.created_at else 'N/A'],
            ['Pages Analyzed:', str(self.site_audit.total_pages or 0)],
            ['Issues Found:', str(self.site_audit.total_issues or 0)],
        ]

        info_table = Table(info_data, colWidths=[1.5*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), BRAND['text_secondary']),
            ('TEXTCOLOR', (1, 0), (1, -1), BRAND['text']),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ]))
        info_table.hAlign = 'CENTER'
        elements.append(info_table)

        elements.append(Spacer(1, 1*inch))

        # Score summary boxes
        scores = [
            ('Performance', self.site_audit.avg_performance),
            ('SEO', self.site_audit.avg_seo),
            ('Accessibility', self.site_audit.avg_accessibility),
            ('Best Practices', self.site_audit.avg_best_practices),
        ]

        score_cells = []
        for label, score in scores:
            score_val = int(score) if score is not None else 0
            color = get_score_color(score)
            cell = Paragraph(
                f"<para alignment='center'><font size='10' color='{BRAND['text_secondary'].hexval()}'>{label}</font><br/>"
                f"<font size='24' color='{color.hexval()}'><b>{score_val}</b></font></para>",
                self.styles['Body']
            )
            score_cells.append(cell)

        score_table = Table([score_cells], colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        score_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOX', (0, 0), (-1, -1), 1, BRAND['border']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BRAND['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('BACKGROUND', (0, 0), (-1, -1), BRAND['light']),
        ]))
        score_table.hAlign = 'CENTER'
        elements.append(score_table)

        return elements

    def _build_executive_summary(self) -> list:
        """Build the executive summary section."""
        elements = []

        elements.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=BRAND['primary'], spaceAfter=15))

        # Overall health assessment
        scores = [
            self.site_audit.avg_performance,
            self.site_audit.avg_seo,
            self.site_audit.avg_accessibility,
            self.site_audit.avg_best_practices
        ]
        valid_scores = [s for s in scores if s is not None]
        overall = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        if overall >= 90:
            health = "Excellent"
            health_color = BRAND['success']
            health_desc = "Your website is performing exceptionally well across all metrics."
        elif overall >= 70:
            health = "Good"
            health_color = BRAND['success']
            health_desc = "Your website is performing well with minor areas for improvement."
        elif overall >= 50:
            health = "Needs Improvement"
            health_color = BRAND['warning']
            health_desc = "Your website has several areas that need attention to improve rankings."
        else:
            health = "Critical"
            health_color = BRAND['danger']
            health_desc = "Your website requires immediate attention to improve search visibility."

        # Health box
        health_table = Table([[
            Paragraph(f"<b>Overall Health:</b>", self.styles['Body']),
            Paragraph(f"<font color='{health_color.hexval()}'><b>{health}</b></font>", self.styles['Body']),
        ]], colWidths=[1.5*inch, 4.5*inch])
        health_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BRAND['light']),
            ('BOX', (0, 0), (-1, -1), 1, BRAND['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(health_table)
        elements.append(Spacer(1, 0.1*inch))
        elements.append(Paragraph(health_desc, self.styles['Body']))

        elements.append(Spacer(1, 0.3*inch))

        # Key Findings
        elements.append(Paragraph("Key Findings", self.styles['SubsectionTitle']))

        findings = []

        # Performance finding
        perf = self.site_audit.avg_performance or 0
        if perf >= 90:
            findings.append(f"<b>Performance ({int(perf)}/100):</b> Excellent loading speeds and responsiveness.")
        elif perf >= 50:
            findings.append(f"<b>Performance ({int(perf)}/100):</b> Room for improvement in loading speeds and interactivity.")
        else:
            findings.append(f"<b>Performance ({int(perf)}/100):</b> Critical performance issues affecting user experience.")

        # SEO finding
        seo = self.site_audit.avg_seo or 0
        if seo >= 90:
            findings.append(f"<b>SEO ({int(seo)}/100):</b> Excellent search engine optimization.")
        elif seo >= 50:
            findings.append(f"<b>SEO ({int(seo)}/100):</b> Good SEO with room for improvement.")
        else:
            findings.append(f"<b>SEO ({int(seo)}/100):</b> SEO issues affecting search visibility.")

        # Accessibility finding
        access = self.site_audit.avg_accessibility or 0
        if access >= 90:
            findings.append(f"<b>Accessibility ({int(access)}/100):</b> Excellent accessibility for all users.")
        elif access >= 50:
            findings.append(f"<b>Accessibility ({int(access)}/100):</b> Some accessibility improvements needed.")
        else:
            findings.append(f"<b>Accessibility ({int(access)}/100):</b> Accessibility issues need attention.")

        # Best Practices finding
        bp = self.site_audit.avg_best_practices or 0
        if bp >= 90:
            findings.append(f"<b>Best Practices ({int(bp)}/100):</b> Following modern web standards.")
        elif bp >= 50:
            findings.append(f"<b>Best Practices ({int(bp)}/100):</b> Some standards improvements recommended.")
        else:
            findings.append(f"<b>Best Practices ({int(bp)}/100):</b> Needs to adopt modern best practices.")

        for finding in findings:
            elements.append(Paragraph(f"• {finding}", self.styles['Body']))

        elements.append(Spacer(1, 0.3*inch))

        # Performance Scores with visual bars
        elements.append(Paragraph("Performance Scores", self.styles['SubsectionTitle']))

        score_data = [
            ('Performance', self.site_audit.avg_performance or 0, 'Page load speed, interactivity, and visual stability'),
            ('SEO', self.site_audit.avg_seo or 0, 'Search engine optimization and discoverability'),
            ('Accessibility', self.site_audit.avg_accessibility or 0, 'Usability for people with disabilities'),
            ('Best Practices', self.site_audit.avg_best_practices or 0, 'Modern web development standards'),
        ]

        rows = []
        for name, score, desc in score_data:
            color = get_score_color(score)
            bar = self._create_horizontal_bar(score, width=150, height=10)
            rows.append([
                Paragraph(f"<b>{name}</b>", self.styles['Body']),
                Paragraph(f"<font color='{color.hexval()}'><b>{int(score)}</b></font>", self.styles['Body']),
                bar,
                Paragraph(f"<font size='8' color='{BRAND['text_secondary'].hexval()}'>{desc}</font>", self.styles['Small']),
            ])

        score_table = Table(rows, colWidths=[1.2*inch, 0.4*inch, 2.2*inch, 2.5*inch])
        score_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, BRAND['border']),
        ]))
        elements.append(score_table)

        elements.append(Spacer(1, 0.2*inch))

        # Score Interpretation
        elements.append(Paragraph("Score Interpretation", self.styles['SubsectionTitle']))

        interp_data = [
            [Paragraph(f"<font color='{BRAND['success'].hexval()}'><b>90-100</b></font>", self.styles['Body']),
             Paragraph("Good - No action needed", self.styles['Body'])],
            [Paragraph(f"<font color='{BRAND['warning'].hexval()}'><b>50-89</b></font>", self.styles['Body']),
             Paragraph("Needs Improvement - Should be addressed", self.styles['Body'])],
            [Paragraph(f"<font color='{BRAND['danger'].hexval()}'><b>0-49</b></font>", self.styles['Body']),
             Paragraph("Poor - Requires immediate attention", self.styles['Body'])],
        ]

        interp_table = Table(interp_data, colWidths=[1*inch, 5*inch])
        interp_table.setStyle(TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ]))
        elements.append(interp_table)

        return elements

    def _build_core_web_vitals(self) -> list:
        """Build the Core Web Vitals section."""
        elements = []

        elements.append(Paragraph("Core Web Vitals", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=BRAND['primary'], spaceAfter=10))
        elements.append(Paragraph(
            "Core Web Vitals are Google's essential metrics for user experience. These directly impact your search rankings.",
            self.styles['SectionSubtitle']
        ))

        # Get page audits
        page_audits = list(self.site_audit.page_audits.all()[:15])

        if not page_audits:
            elements.append(Paragraph("No Core Web Vitals data available.", self.styles['Body']))
            return elements

        # Calculate averages
        metrics = {
            'lcp': [], 'cls': [], 'tbt': [], 'fcp': [], 'si': [], 'ttfb': []
        }

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

        # CWV definitions
        cwv_info = [
            ('LCP', 'Largest Contentful Paint', 'lcp', 's',
             'Measures loading performance. The main content should load quickly.'),
            ('CLS', 'Cumulative Layout Shift', 'cls', '',
             'Measures visual stability. Page elements should not shift during loading.'),
            ('TBT', 'Total Blocking Time', 'tbt', 'ms',
             'Measures interactivity. Scripts should not block user interactions.'),
            ('FCP', 'First Contentful Paint', 'fcp', 's',
             'First content rendered. Users should see feedback quickly.'),
            ('SI', 'Speed Index', 'si', 's',
             'Visual progress speed. Content should appear progressively.'),
        ]

        # Header row
        header = [
            Paragraph("<b>Metric</b>", self.styles['TableHeader']),
            Paragraph("<b>Value</b>", self.styles['TableHeader']),
            Paragraph("<b>Status</b>", self.styles['TableHeader']),
            Paragraph("<b>Description</b>", self.styles['TableHeader']),
        ]

        rows = [header]

        for abbr, full_name, key, unit, desc in cwv_info:
            values = metrics.get(key, [])
            if values:
                avg_val = sum(values) / len(values)
                status, color, threshold_desc = get_cwv_status(key, avg_val)

                # Format value
                if key == 'cls':
                    val_str = f"{avg_val:.3f}"
                elif unit == 'ms':
                    val_str = f"{int(avg_val)}ms"
                else:
                    val_str = f"{avg_val:.2f}s"

                rows.append([
                    Paragraph(f"<b>{abbr}</b><br/><font size='8' color='{BRAND['text_secondary'].hexval()}'>{full_name}</font>",
                             self.styles['Body']),
                    Paragraph(f"<font color='{color.hexval()}'><b>{val_str}</b></font>", self.styles['Body']),
                    Paragraph(f"<font color='{color.hexval()}'>{status}</font>", self.styles['Body']),
                    Paragraph(f"{desc}<br/><font size='8' color='{BRAND['text_secondary'].hexval()}'>{threshold_desc}</font>",
                             self.styles['Small']),
                ])

        if len(rows) > 1:
            cwv_table = Table(rows, colWidths=[1.5*inch, 0.8*inch, 0.9*inch, 3.2*inch])
            cwv_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), BRAND['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), BRAND['white']),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, BRAND['border']),
                ('BOX', (0, 0), (-1, -1), 1, BRAND['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRAND['white'], BRAND['light']]),
            ]))
            elements.append(cwv_table)
        else:
            elements.append(Paragraph("No Core Web Vitals data available.", self.styles['Body']))

        return elements

    def _build_issues_section(self) -> list:
        """Build the issues overview section."""
        from ..models import AuditIssue

        elements = []

        elements.append(Paragraph("Issues Overview", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=BRAND['primary'], spaceAfter=15))

        # Issues by Severity
        elements.append(Paragraph("Issues by Severity", self.styles['SubsectionTitle']))

        critical = self.site_audit.critical_issues or 0
        warnings = self.site_audit.warning_issues or 0
        info_count = (self.site_audit.total_issues or 0) - critical - warnings
        if info_count < 0:
            info_count = 0

        severity_data = [[
            Paragraph(f"<para alignment='center'><font color='{BRAND['danger'].hexval()}'><b>Errors</b></font></para>", self.styles['Body']),
            Paragraph(f"<para alignment='center'><font color='{BRAND['warning'].hexval()}'><b>Warnings</b></font></para>", self.styles['Body']),
            Paragraph(f"<para alignment='center'><font color='{BRAND['info'].hexval()}'><b>Info</b></font></para>", self.styles['Body']),
        ], [
            Paragraph(f"<para alignment='center'><font size='20' color='{BRAND['danger'].hexval()}'><b>{critical}</b></font></para>", self.styles['Body']),
            Paragraph(f"<para alignment='center'><font size='20' color='{BRAND['warning'].hexval()}'><b>{warnings}</b></font></para>", self.styles['Body']),
            Paragraph(f"<para alignment='center'><font size='20' color='{BRAND['info'].hexval()}'><b>{info_count}</b></font></para>", self.styles['Body']),
        ]]

        severity_table = Table(severity_data, colWidths=[2*inch, 2*inch, 2*inch])
        severity_table.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, -1), 1, BRAND['border']),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BRAND['border']),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('BACKGROUND', (0, 0), (-1, 0), BRAND['light']),
        ]))
        elements.append(severity_table)

        elements.append(Spacer(1, 0.3*inch))

        # Issues by Category
        elements.append(Paragraph("Issues by Category", self.styles['SubsectionTitle']))

        # Get issues grouped by category
        issues = AuditIssue.objects.filter(
            page_audit__site_audit=self.site_audit
        ).exclude(severity='passed')

        categories = {}
        for issue in issues:
            cat = issue.category or 'general'
            categories[cat] = categories.get(cat, 0) + 1

        cat_header = [
            Paragraph("<b>Category</b>", self.styles['TableHeader']),
            Paragraph("<b>Issues</b>", self.styles['TableHeader']),
            Paragraph("<b>Description</b>", self.styles['TableHeader']),
        ]

        cat_descriptions = {
            'performance': 'Speed, loading, and responsiveness issues',
            'seo': 'Search engine optimization issues',
            'accessibility': 'Issues affecting users with disabilities',
            'best-practices': 'Modern web standards and security',
            'general': 'General website issues',
        }

        cat_rows = [cat_header]
        if categories:
            for cat, count in sorted(categories.items()):
                cat_rows.append([
                    Paragraph(f"<b>{cat.replace('-', ' ').title()}</b>", self.styles['Body']),
                    Paragraph(str(count), self.styles['Body']),
                    Paragraph(cat_descriptions.get(cat, 'Other issues'), self.styles['Small']),
                ])
        else:
            # Show default categories with 0
            for cat in ['performance', 'seo', 'accessibility', 'best-practices']:
                cat_rows.append([
                    Paragraph(f"<b>{cat.replace('-', ' ').title()}</b>", self.styles['Body']),
                    Paragraph("0", self.styles['Body']),
                    Paragraph(cat_descriptions.get(cat, ''), self.styles['Small']),
                ])

        cat_table = Table(cat_rows, colWidths=[1.5*inch, 0.8*inch, 4*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), BRAND['white']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, BRAND['border']),
            ('BOX', (0, 0), (-1, -1), 1, BRAND['border']),
        ]))
        elements.append(cat_table)

        # Detailed Issues List (if any)
        if issues.exists():
            elements.append(Spacer(1, 0.3*inch))
            elements.append(Paragraph("Detailed Issues", self.styles['SubsectionTitle']))

            detail_header = [
                Paragraph("<b>Issue</b>", self.styles['TableHeader']),
                Paragraph("<b>Severity</b>", self.styles['TableHeader']),
                Paragraph("<b>Category</b>", self.styles['TableHeader']),
                Paragraph("<b>Description</b>", self.styles['TableHeader']),
            ]

            detail_rows = [detail_header]
            for issue in issues[:20]:  # Limit to 20 issues
                title = (issue.title or 'Unknown Issue')[:35]
                if len(issue.title or '') > 35:
                    title += '...'

                severity = issue.severity or 'info'
                sev_color = BRAND['danger'] if severity == 'error' else (
                    BRAND['warning'] if severity == 'warning' else BRAND['info']
                )

                desc = (issue.description or '')[:80]
                if len(issue.description or '') > 80:
                    desc += '...'

                detail_rows.append([
                    Paragraph(f"<font size='8'>{title}</font>", self.styles['Body']),
                    Paragraph(f"<font size='8' color='{sev_color.hexval()}'>{severity.title()}</font>", self.styles['Body']),
                    Paragraph(f"<font size='8'>{(issue.category or 'general').title()}</font>", self.styles['Body']),
                    Paragraph(f"<font size='8'>{desc}</font>", self.styles['Small']),
                ])

            detail_table = Table(detail_rows, colWidths=[1.5*inch, 0.7*inch, 0.9*inch, 3.2*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), BRAND['primary']),
                ('TEXTCOLOR', (0, 0), (-1, 0), BRAND['white']),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('LINEBELOW', (0, 0), (-1, -1), 0.5, BRAND['border']),
                ('BOX', (0, 0), (-1, -1), 1, BRAND['border']),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRAND['white'], BRAND['light']]),
            ]))
            elements.append(detail_table)

        return elements

    def _build_audited_pages(self) -> list:
        """Build the audited pages section."""
        elements = []

        total_pages = self.site_audit.total_pages or 0
        elements.append(Paragraph("Audited Pages", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=BRAND['primary'], spaceAfter=10))
        elements.append(Paragraph(
            f"This section lists all {total_pages} pages that were audited, showing individual performance scores for each URL.",
            self.styles['SectionSubtitle']
        ))

        page_audits = list(self.site_audit.page_audits.all())

        if not page_audits:
            elements.append(Paragraph("No pages audited.", self.styles['Body']))
            return elements

        # Header
        header = [
            Paragraph("<b>URL</b>", self.styles['TableHeader']),
            Paragraph("<b>Perf</b>", self.styles['TableHeader']),
            Paragraph("<b>SEO</b>", self.styles['TableHeader']),
            Paragraph("<b>Access</b>", self.styles['TableHeader']),
            Paragraph("<b>BP</b>", self.styles['TableHeader']),
        ]

        rows = [header]

        for page in page_audits:
            # Truncate URL
            url = page.url or 'Unknown URL'
            if len(url) > 45:
                url = url[:42] + '...'

            def format_score(score):
                if score is None:
                    return Paragraph("N/A", self.styles['TableCell'])
                color = get_score_color(score)
                return Paragraph(f"<font color='{color.hexval()}'><b>{int(score)}</b></font>", self.styles['TableCell'])

            rows.append([
                Paragraph(f"<font size='8' color='{BRAND['primary'].hexval()}'>{url}</font>", self.styles['URL']),
                format_score(page.performance_score),
                format_score(page.seo_score),
                format_score(page.accessibility_score),
                format_score(page.best_practices_score),
            ])

        page_table = Table(rows, colWidths=[3.2*inch, 0.6*inch, 0.6*inch, 0.7*inch, 0.6*inch])
        page_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BRAND['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), BRAND['white']),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('LINEBELOW', (0, 0), (-1, -1), 0.5, BRAND['border']),
            ('BOX', (0, 0), (-1, -1), 1, BRAND['border']),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRAND['white'], BRAND['light']]),
        ]))
        elements.append(page_table)

        return elements

    def _build_ai_analysis(self) -> list:
        """Build the AI analysis section."""
        elements = []

        elements.append(Paragraph("AI-Powered Analysis & Recommendations", self.styles['SectionTitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=BRAND['primary'], spaceAfter=10))
        elements.append(Paragraph(
            "The following analysis was generated by AI based on your audit results:",
            self.styles['SectionSubtitle']
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
                elements.append(Paragraph(line[4:], self.styles['SubsectionTitle']))
            elif line.startswith('## '):
                elements.append(Paragraph(line[3:], self.styles['SubsectionTitle']))
            elif line.startswith('# '):
                elements.append(Spacer(1, 0.1*inch))
                elements.append(Paragraph(
                    f"<font color='{BRAND['primary'].hexval()}'><b>{line[2:]}</b></font>",
                    self.styles['SubsectionTitle']
                ))
            elif line.startswith('- ') or line.startswith('* '):
                elements.append(Paragraph(f"• {line[2:]}", self.styles['Body']))
            elif line.startswith('|'):
                # Skip markdown table formatting
                continue
            elif line.startswith('```'):
                continue
            else:
                # Handle bold/italic markdown
                import re
                line = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', line)
                line = re.sub(r'\*([^*]+)\*', r'<i>\1</i>', line)
                elements.append(Paragraph(line, self.styles['Body']))

        return elements


def generate_seo_audit_pdf(site_audit) -> bytes:
    """
    Convenience function to generate a PDF report.

    Args:
        site_audit: SiteAudit model instance

    Returns:
        PDF content as bytes
    """
    generator = PremiumSEOReportGenerator(site_audit)
    return generator.generate()
