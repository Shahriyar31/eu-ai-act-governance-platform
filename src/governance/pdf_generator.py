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
from src.governance.translation import translate

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
    output_dir: str = "src/reports",
    language: str = "en"
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
    _add_cover_page(story, styles, system_name, classification, language)
    _add_executive_summary(story, styles, classification, dpia, owasp, nist, language)
    _add_classification_section(story, styles, classification, language)
    _add_dpia_section(story, styles, dpia, language)
    _add_owasp_section(story, styles, owasp, language)
    _add_nist_section(story, styles, nist, language)
    _add_recommendations_section(story, styles, classification, dpia, owasp, nist, language)

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


def _add_cover_page(story, styles, system_name, classification, language):
    story.append(Spacer(1, 1*inch))

    story.append(Paragraph(translate("EU AI Act Governance Platform", language), styles['ReportTitle']))
    story.append(Paragraph(translate("AI Compliance Assessment Report", language), styles['ReportTitle']))

    story.append(Spacer(1, 0.5*inch))
    story.append(HRFlowable(width="100%", thickness=2, color=MEDIUM_BLUE))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph(f"{translate('System:', language)} {system_name}", styles['SectionHeader']))

    risk_label = translate(f"{classification.risk_tier.upper()} RISK", language)
    story.append(Paragraph(
        f"{translate('Risk Classification:', language)} {risk_label}",
        styles['SectionHeader']
    ))

    story.append(Spacer(1, 0.3*inch))

    dpia_req_label = translate("Yes" if classification.dpia_required else "No", language)
    meta_data = [
        [translate("Report Generated:", language), datetime.now().strftime("%d %B %Y, %H:%M UTC")],
        [translate("Assessment Framework:", language), "EU AI Act, GDPR Article 35, OWASP LLM Top 10, NIST AI RMF"],
        [translate("Classification:", language), risk_label],
        [translate("DPIA Required:", language), dpia_req_label],
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


def _add_executive_summary(story, styles, classification, dpia, owasp, nist, language):
    story.append(Paragraph(translate("Executive Summary", language), styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))
    story.append(Spacer(1, 0.1*inch))

    risk_label = translate(f"{classification.risk_tier.upper()} RISK", language)
    severity_label = translate(owasp.severity_level.upper(), language)

    if language == "de":
        summary_text = (
            f"Dieser Bericht enthält die Ergebnisse einer Bewertung der KI-Governance und -Compliance "
            f"für <b>{classification.system_name}</b>. "
            f"Das System wurde gemäß dem EU AI Act in die Risikostufe <b>{risk_label}</b> eingestuft. "
            f"{classification.justification} "
            f"Es wurden insgesamt {len(classification.obligations)} Compliance-Verpflichtungen identifiziert. "
        )
        if dpia.dpia_required:
            summary_text += (
                f"Eine Datenschutz-Folgenabschätzung ist gemäß DSGVO Artikel 35 zwingend erforderlich. "
                f"Es wurden {len(dpia.risks_identified)} Datenschutzrisiken identifiziert. "
            )
        summary_text += (
            f"Die OWASP LLM Top 10 Bewertung ergab {len(owasp.risks_found)} Sicherheitsrisiken "
            f"mit einem Gesamtschweregrad von <b>{severity_label}</b>. "
            f"Die NIST AI RMF Bewertung weist folgenden Reifegrad auf: <b>{nist.overall_maturity}</b>. "
            f"Insgesamt erfordern {len(nist.gaps)} Compliance-Lücken sofortige Aufmerksamkeit."
        )
    elif language == "fr":
        summary_text = (
            f"Ce rapport présente les résultats d'une évaluation de la gouvernance et de la conformité de l'IA "
            f"réalisée pour <b>{classification.system_name}</b>. "
            f"Le système a été classé comme <b>{risk_label}</b> "
            f"sous l'EU AI Act. "
            f"{classification.justification} "
            f"Un total de {len(classification.obligations)} obligations de conformité ont été identifiées. "
        )
        if dpia.dpia_required:
            summary_text += (
                f"Une analyse d'impact relative à la protection des données (AIPD) est obligatoire en vertu de l'article 35 du RGPD. "
                f"{len(dpia.risks_identified)} risques liés à la protection des données ont été identifiés. "
            )
        summary_text += (
            f"L'évaluation OWASP LLM Top 10 a identifié {len(owasp.risks_found)} risques de sécurité "
            f"avec un niveau de gravité global de <b>{severity_label}</b>. "
            f"L'évaluation de maturité NIST AI RMF indique: <b>{nist.overall_maturity}</b>. "
            f"Un total de {len(nist.gaps)} écarts de conformité nécessitent une attention immédiate."
        )
    elif language == "es":
        summary_text = (
            f"Este informe presenta los resultados de una evaluación de gobernanza y cumplimiento de IA "
            f"realizada para <b>{classification.system_name}</b>. "
            f"El sistema ha sido clasificado como <b>{risk_label}</b> "
            f"bajo la Ley de IA de la UE. "
            f"{classification.justification} "
            f"Se han identificado un total de {len(classification.obligations)} obligaciones de cumplimiento. "
        )
        if dpia.dpia_required:
            summary_text += (
                f"Es obligatoria una Evaluación de Impacto de Protección de Datos según el Artículo 35 del RGPD. "
                f"Se han identificado {len(dpia.risks_identified)} riesgos de protección de datos. "
            )
        summary_text += (
            f"La evaluación OWASP LLM Top 10 identificó {len(owasp.risks_found)} riesgos de seguridad "
            f"con una gravedad global de <b>{severity_label}</b>. "
            f"La evaluación de madurez de NIST AI RMF indica: <b>{nist.overall_maturity}</b>. "
            f"Un total de {len(nist.gaps)} brechas de cumplimiento requieren atención inmediata."
        )
    else:
        summary_text = (
            f"This report presents the results of an AI governance and compliance assessment "
            f"conducted for <b>{classification.system_name}</b>. "
            f"The system has been classified as <b>{risk_label}</b> "
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
            f"with an overall severity of <b>{severity_label}</b>. "
            f"The NIST AI RMF maturity assessment indicates: <b>{nist.overall_maturity}</b>. "
            f"A total of {len(nist.gaps)} compliance gaps require immediate attention."
        )

    story.append(Paragraph(summary_text, styles['BodyText2']))


def _add_classification_section(story, styles, classification, language):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(translate("1. EU AI Act Risk Classification", language), styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    risk_label = translate(f"{classification.risk_tier.upper()} RISK", language)
    dpia_req_label = translate("Yes" if classification.dpia_required else "No", language)

    story.append(Paragraph(f"<b>{translate('Risk Tier:', language)}</b> {risk_label}", styles['BodyText2']))
    story.append(Paragraph(f"<b>{translate('Justification:', language)}</b> {translate(classification.justification, language)}", styles['BodyText2']))
    story.append(Paragraph(f"<b>{translate('DPIA Required:', language)}</b> {dpia_req_label}", styles['BodyText2']))

    story.append(Paragraph(translate("Compliance Obligations:", language), styles['SubHeader']))
    for obligation in classification.obligations:
        story.append(Paragraph(f"• {translate(obligation, language)}", styles['BulletText']))


def _add_dpia_section(story, styles, dpia, language):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(translate("2. Data Protection Impact Assessment", language), styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    story.append(Paragraph(translate(dpia.assessment_summary, language), styles['BodyText2']))

    if dpia.risks_identified:
        story.append(Paragraph(translate("Risks Identified:", language), styles['SubHeader']))
        for risk in dpia.risks_identified:
            story.append(Paragraph(f"• {translate(risk, language)}", styles['BulletText']))

    if dpia.mitigation_measures:
        story.append(Paragraph(translate("Mitigation Measures:", language), styles['SubHeader']))
        for measure in dpia.mitigation_measures:
            story.append(Paragraph(f"• {translate(measure, language)}", styles['BulletText']))

    story.append(Paragraph(f"<b>{translate('Recommendation:', language)}</b> {translate(dpia.recommendation, language)}", styles['BodyText2']))


def _add_owasp_section(story, styles, owasp, language):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(translate("3. OWASP LLM Top 10 Security Assessment", language), styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    severity_label = translate(owasp.severity_level.upper(), language)
    story.append(Paragraph(
        f"<b>{translate('Overall Security Severity:', language)}</b> <b>{severity_label}</b>",
        styles['BodyText2']
    ))

    if owasp.risks_found:
        story.append(Paragraph(translate("Security Risks Identified:", language), styles['SubHeader']))
        for risk in owasp.risks_found:
            story.append(Paragraph(f"• {translate(risk, language)}", styles['BulletText']))

    if owasp.recommendations:
        story.append(Paragraph(translate("Security Recommendations:", language), styles['SubHeader']))
        for rec in owasp.recommendations:
            story.append(Paragraph(f"• {translate(rec, language)}", styles['BulletText']))


def _add_nist_section(story, styles, nist, language):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(translate("4. NIST AI RMF Assessment", language), styles['SectionHeader']))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_BLUE))

    story.append(Paragraph(
        f"<b>{translate('Overall Maturity Level:', language)}</b> {translate(nist.overall_maturity, language)}",
        styles['BodyText2']
    ))

    sections = [
        ("GOVERN Controls:", nist.govern),
        ("MAP Controls:", nist.map),
        ("MEASURE Controls:", nist.measure),
        ("MANAGE Controls:", nist.manage)
    ]

    for section_name, controls in sections:
        if controls:
            story.append(Paragraph(translate(section_name, language), styles['SubHeader']))
            for control in controls:
                story.append(Paragraph(f"• {translate(control, language)}", styles['BulletText']))

    if nist.gaps:
        story.append(Paragraph(translate("Compliance Gaps:", language), styles['SubHeader']))
        for gap in nist.gaps:
            story.append(Paragraph(f"• {translate(gap, language)}", styles['BulletText']))


def _add_recommendations_section(story, styles, classification, dpia, owasp, nist, language):
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph(translate("5. Priority Recommendations", language), styles['SectionHeader']))
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
        story.append(Paragraph(f"• {translate(action, language)}", styles['BulletText']))