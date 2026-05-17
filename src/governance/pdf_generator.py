from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os
from datetime import datetime
from src.governance.nist import NISTAssessment
from src.models.schemas import ClassificationResponse, DPIAResponse, OWASPResponse

# Colour palette
DARK_BLUE = HexColor('#1a2f5a')
MEDIUM_BLUE = HexColor('#2563eb')
LIGHT_BLUE = HexColor('#eff6ff')
RED = HexColor('#dc2626')
ORANGE = HexColor('#ea580c')
GREEN = HexColor('#16a34a')
YELLOW = HexColor('#ca8a04')
LIGHT_GREY = HexColor('#f8fafc')
DARK_GREY = HexColor('#374151')

RISK_COLOURS = {
    "unacceptable": RED,
    "high": ORANGE,
    "limited": YELLOW,
    "minimal": GREEN
}


def generate_pdf_report(
    system_name: str,
    classification: ClassificationResponse,
    dpia: DPIAResponse,
    owasp: OWASPResponse,
    nist: NISTAssessment,
    output_dir: str = "src/reports"
) -> str:

    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{system_name.replace(' ', '_')}_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )

    styles = _create_styles()
    story = []

    # Build report sections
    _add_cover_page(story, styles, system_name, classification)
    _add_executive_summary(story, styles, classification, dpia, owasp, nist)
    _add_classification_section(story, styles, classification)
    _add_dpia_section(story, styles, dpia)
    _add_owasp_section(story, styles, owasp)
    _add_nist_section(story, styles, nist)
    _add_recommendations_section(story, styles, classification, dpia, owasp, nist)

    doc.build(story)
    return filepath


def _create_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name='ReportTitle',
        fontSize=24,
        textColor=DARK_BLUE,
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontSize=14,
        textColor=DARK_BLUE,
        spaceBefore=16,
        spaceAfter=8,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='SubHeader',
        fontSize=11,
        textColor=DARK_GREY,
        spaceBefore=10,
        spaceAfter=6,
        fontName='Helvetica-Bold'
    ))

    styles.add(ParagraphStyle(
        name='BodyText2',
        fontSize=10,
        textColor=DARK_GREY,
        spaceAfter=6,
        leading=14
    ))

    styles.add(ParagraphStyle(
        name='BulletText',
        fontSize=9,
        textColor=DARK_GREY,
        spaceAfter=4,
        leftIndent=20,
        leading=13
    ))

    return styles


def _add_cover_page(story, styles, system_name, classification):
    story.append(Spacer(1, 1*inch))

    story.append(Paragraph("EU AI Act Governance Platform", styles['ReportTitle']))
    story.append(Paragraph("AI Compliance Assessment Report", styles['ReportTitle']))

    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", thickness=2, color=MEDIUM_BLUE))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(f"System: {system_name}", styles['SectionHeader']))

    risk_colour = RISK_COLOURS.get(classification.risk_tier.lower(), DARK_GREY)
    story.append(Paragraph(
        f"Risk Classification: {classification.risk_tier.upper()} RISK",
        styles['SectionHeader']
    ))

    story.append(Spacer(1, 0.3*inch))

    meta_data = [
        ["Report Generated:", datetime.now().strftime("%d %B %Y, %H:%M UTC")],
        ["Assessment Framework:", "EU AI Act, GDPR Article 35, OWASP LLM Top 10, NIST AI RMF"],
        ["Classification:", f"{classification.risk_tier.upper()} RISK"],
        ["DPIA Required:", "Yes" if classification.dpia_required else "No"],
    ]

    table = Table(meta_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (0, -1), DARK_BLUE),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [LIGHT_GREY, None]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))


def _add_executive_summary(story, styles, classification, dpia, owasp, nist):
    story.append(Paragraph("Executive Summary", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))
    story.append(Spacer(1, 0.1*inch))

    summary_text = (
        f"This report presents the results of an AI governance and compliance assessment "
        f"conducted for <b>{classification.system_name}</b>. "
        f"The system has been classified as <b>{classification.risk_tier.upper()} RISK</b> "
        f"under the EU AI Act. "
        f"{classification.justification} "
        f"A total of {len(classification.obligations)} compliance obligations have been identified. "
    )

    if dpia.dpia_required:
        summary_text += (
            f"A Data Protection Impact Assessment is mandatory under GDPR Article 35. "
            f"{len(dpia.risks_identified)} data protection risks have been identified. "
        )

    summary_text += (
        f"The OWASP LLM Top 10 assessment identified {len(owasp.risks_found)} security risks "
        f"with an overall severity of <b>{owasp.severity_level.upper()}</b>. "
        f"The NIST AI RMF maturity assessment indicates: <b>{nist.overall_maturity}</b>. "
        f"A total of {len(nist.gaps)} compliance gaps require immediate attention."
    )

    story.append(Paragraph(summary_text, styles['BodyText2']))


def _add_classification_section(story, styles, classification):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("1. EU AI Act Risk Classification", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    story.append(Paragraph(f"<b>Risk Tier:</b> {classification.risk_tier.upper()}", styles['BodyText2']))
    story.append(Paragraph(f"<b>Justification:</b> {classification.justification}", styles['BodyText2']))
    story.append(Paragraph(f"<b>DPIA Required:</b> {'Yes' if classification.dpia_required else 'No'}", styles['BodyText2']))

    story.append(Paragraph("Compliance Obligations:", styles['SubHeader']))
    for obligation in classification.obligations:
        story.append(Paragraph(f"• {obligation}", styles['BulletText']))


def _add_dpia_section(story, styles, dpia):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("2. Data Protection Impact Assessment", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    story.append(Paragraph(dpia.assessment_summary, styles['BodyText2']))

    if dpia.risks_identified:
        story.append(Paragraph("Risks Identified:", styles['SubHeader']))
        for risk in dpia.risks_identified:
            story.append(Paragraph(f"• {risk}", styles['BulletText']))

    if dpia.mitigation_measures:
        story.append(Paragraph("Mitigation Measures:", styles['SubHeader']))
        for measure in dpia.mitigation_measures:
            story.append(Paragraph(f"• {measure}", styles['BulletText']))

    story.append(Paragraph(f"<b>Recommendation:</b> {dpia.recommendation}", styles['BodyText2']))


def _add_owasp_section(story, styles, owasp):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("3. OWASP LLM Top 10 Security Assessment", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    story.append(Paragraph(
        f"Overall Security Severity: <b>{owasp.severity_level.upper()}</b>",
        styles['BodyText2']
    ))

    if owasp.risks_found:
        story.append(Paragraph("Security Risks Identified:", styles['SubHeader']))
        for risk in owasp.risks_found:
            story.append(Paragraph(f"• {risk}", styles['BulletText']))

    if owasp.recommendations:
        story.append(Paragraph("Security Recommendations:", styles['SubHeader']))
        for rec in owasp.recommendations:
            story.append(Paragraph(f"• {rec}", styles['BulletText']))


def _add_nist_section(story, styles, nist):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("4. NIST AI RMF Assessment", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    story.append(Paragraph(
        f"<b>Overall Maturity Level:</b> {nist.overall_maturity}",
        styles['BodyText2']
    ))

    sections = [
        ("GOVERN", nist.govern),
        ("MAP", nist.map),
        ("MEASURE", nist.measure),
        ("MANAGE", nist.manage)
    ]

    for section_name, controls in sections:
        if controls:
            story.append(Paragraph(f"{section_name} Controls:", styles['SubHeader']))
            for control in controls:
                story.append(Paragraph(f"• {control}", styles['BulletText']))

    if nist.gaps:
        story.append(Paragraph("Compliance Gaps:", styles['SubHeader']))
        for gap in nist.gaps:
            story.append(Paragraph(f"• {gap}", styles['BulletText']))


def _add_recommendations_section(story, styles, classification, dpia, owasp, nist):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("5. Priority Recommendations", styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    priority_actions = []

    if classification.risk_tier == "unacceptable":
        priority_actions.append("IMMEDIATE: Cease all development and deployment of this system")

    if classification.risk_tier == "high":
        priority_actions.append("HIGH: Complete EU AI Act registration before deployment")
        priority_actions.append("HIGH: Implement human oversight mechanism")

    if dpia.dpia_required:
        priority_actions.append("HIGH: Complete and document DPIA before processing personal data")

    if owasp.severity_level == "critical":
        priority_actions.append("HIGH: Address all Critical OWASP LLM security findings immediately")

    if nist.gaps:
        for gap in nist.gaps[:3]:
            priority_actions.append(f"REQUIRED: {gap}")

    priority_actions.append("ONGOING: Review this assessment annually or when system changes significantly")
    priority_actions.append("ONGOING: Monitor EU AI Act guidance as implementing regulations are published")

    for action in priority_actions:
        story.append(Paragraph(f"• {action}", styles['BulletText']))