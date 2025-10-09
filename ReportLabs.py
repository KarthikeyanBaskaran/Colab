import yaml
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY
from io import BytesIO
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

# Load YAML
def load_content(yaml_file):
    with open(yaml_file, "r") as f:
        return yaml.safe_load(f)

def build_pdf(data, output_file="resume.pdf"):
    width, _ = A4
    leftMargin = 40
    rightMargin = 40
    topMargin = 40
    bottomMargin = 40
    availWidth = width - leftMargin - rightMargin

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    section_style = ParagraphStyle("Section", fontSize=12, textColor=colors.black, spaceAfter=6, leading=16, spaceBefore=12)
    text_style = ParagraphStyle("Text", fontSize=10, leading=14)
    justified_style = ParagraphStyle("Justified", fontSize=10, leading=14, alignment=TA_JUSTIFY)
    bullet_style = ParagraphStyle("Bullet", fontSize=10, leading=14, leftIndent=15, bulletIndent=5, alignment=TA_JUSTIFY)
    big_bold_style = ParagraphStyle(
        name='BigBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=22,
        textColor=colors.black,
        alignment=1  # Left aligned
    )

    left_normal_style = ParagraphStyle(
        name='LeftNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.black,
        alignment=0
    )

    right_normal_style = ParagraphStyle(
        name='RightNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.black,
        alignment=2  # Right aligned
    )

    # Header
    elements.append(Paragraph('Karthikeyan Baskaran', big_bold_style))
    left_col = [
        Paragraph('karthikeyanbaskarca@gmail.com', left_normal_style),
        Paragraph('+1 437-665-6654', left_normal_style)
]

    right_col = [
        Paragraph('<link href="https://linkedin.com/in/karthikeyan-baskaran-data/">linkedin.com/in/karthikeyan-baskaran</link>', right_normal_style),
        Paragraph('<link href="https://github.com/KarthikeyanBaskaran"> github.com/KarthikeyanBaskaran</link>', right_normal_style)
    ]

    # Combine into table
    header_data = [[left, right] for left, right in zip(left_col, right_col)]
    header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch], hAlign='CENTER')

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.transparent),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))

    elements.append(header_table)

    # ---- SUMMARY ----
    elements.append(Paragraph("Summary", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.75, lineCap='round', color='black'))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(data["summary"], justified_style))

    # ---- SKILLS ----
    elements.append(Paragraph("Skills", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.75, lineCap='round', color='black'))
    elements.append(Spacer(1, 4))

    for item in data.get("skills", []):
        category = item.get("name", "Skills")
        keywords = item.get("keywords", [])
        elements.append(Paragraph(f"<b>{category}:</b> {', '.join(map(str, keywords))}", text_style))

    # ---- WORK EXPERIENCE ----
    elements.append(Paragraph("Work Experience", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.75, lineCap='round', color='black'))
    elements.append(Spacer(1, 4))

    hardcoded_jobs = [
        {"title": "Purchaser in Global Procurement", "company": "Vestas Wind Systems", "dates": "Nov 2021 - Aug 2023"},
        {"title": "Consultant ECM Purchaser in Global Procurement,Vestas", "company": "ManpowerGroup Services", "dates": "Jan 2021 - Nov 2021"},
        {"title": "Procurement Engineer(Intern) - Global Sourcing", "company": "Valeo India", "dates": "Jan 2019 - Jan 2021"}
    ]

    for idx, job in enumerate(hardcoded_jobs):
        workleft_col = [
              Paragraph(f"<b>{job['title']}</b>", left_normal_style)
          ]
        workright_col = [
              Paragraph(job['dates'], right_normal_style)
          ]

        header_data = [[left, right] for left, right in zip(workleft_col, workright_col)]
        header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch], hAlign='CENTER')

        header_table.setStyle(TableStyle([
          ('VALIGN', (0, 0), (-1, -1), 'TOP'),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.transparent),
          ('LEFTPADDING', (0, 0), (-1, -1), 0),
          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
          ('TOPPADDING', (0, 0), (-1, -1), 0),
          ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
      ]))

        elements.append(header_table)
        elements.append(Paragraph(job['company'], text_style))
        yaml_job = data['work_experience'][idx]
        bullet_points = [ListItem(Paragraph(bp, bullet_style)) for bp in yaml_job["achievements"]]
        elements.append(ListFlowable(bullet_points, bulletType="bullet", start="•"))
        elements.append(Spacer(1, 6))

    # ---- PROJECTS ----
    elements.append(Paragraph("Projects", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.75, lineCap='round', color='black'))
    elements.append(Spacer(1, 4))

    for proj in data["projects"]:
        elements.append(Paragraph(f"<b>{proj['project_name']}</b>", text_style))
        elements.append(Paragraph(proj["description"], justified_style))
        elements.append(Paragraph(f"({', '.join(proj['keywords'])})", text_style))
        elements.append(Spacer(1, 6))

    # ---- EDUCATION ----
    elements.append(Paragraph("Education", section_style))
    elements.append(HRFlowable(width="100%", thickness=0.75, lineCap='round', color='black'))
    elements.append(Spacer(1, 4))

    hardcoded_education = [
        {"degree": " Post Grad Diploma in Data Analytics for Business", "institution": "St. Clair College, Canada", "gpa": "4.0 ", "dates": "Sep 2023 - Apr 2025"},
        {"degree": "Bachelor of Mechanical Engineering", "institution": "St. Joseph's Institute of Technology, India", "gpa": "3.7", "dates": "Jun 2014 - Jun 2018"}
    ]

    for edu in hardcoded_education:
      left_col = [
        Paragraph(f'<b>{edu['degree']}</b>', left_normal_style),
        Paragraph(f'{edu['institution']}', left_normal_style)
        ]
      right_col = [
          Paragraph(f'GPA: {edu['gpa']} / 4.0 ', right_normal_style),
          Paragraph(f'{edu['dates']}', right_normal_style)
      ]

      header_data = [[left, right] for left, right in zip(left_col, right_col)]
      header_table = Table(header_data, colWidths=[3.5*inch, 3.5*inch], hAlign='CENTER')

      header_table.setStyle(TableStyle([
          ('VALIGN', (0, 0), (-1, -1), 'TOP'),
          ('GRID', (0, 0), (-1, -1), 0.5, colors.transparent),
          ('LEFTPADDING', (0, 0), (-1, -1), 0),
          ('RIGHTPADDING', (0, 0), (-1, -1), 0),
          ('TOPPADDING', (0, 0), (-1, -1), 0),
          ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
      ]))

      elements.append(header_table)
      elements.append(Spacer(1, 6))

    # Create dummy canvas for height calculation
    buffer = BytesIO()
    dummy_canv = canvas.Canvas(buffer)

    # Calculate total height
    total_height = 0
    for elem in elements:
        if hasattr(elem, 'wrapOn'):
            w, h = elem.wrapOn(dummy_canv, availWidth, 100000)
        else:
            original_canv = getattr(elem, 'canv', None)
            original__canv = getattr(elem, '_canv', None)
            setattr(elem, 'canv', dummy_canv)
            setattr(elem, '_canv', dummy_canv)
            w, h = elem.wrap(availWidth, 100000)
            if original_canv is None:
                if hasattr(elem, 'canv'):
                    delattr(elem, 'canv')
            else:
                setattr(elem, 'canv', original_canv)
            if original__canv is None:
                if hasattr(elem, '_canv'):
                    delattr(elem, '_canv')
            else:
                setattr(elem, '_canv', original__canv)
        total_height += elem.getSpaceBefore() + h + elem.getSpaceAfter()

    page_height = total_height + topMargin + bottomMargin + 20

    # Create temporary PDF
    temp_output = "temp_resume.pdf"
    doc = SimpleDocTemplate(temp_output, pagesize=(width, page_height),
                            leftMargin=leftMargin, rightMargin=rightMargin,
                            topMargin=topMargin, bottomMargin=bottomMargin)

    # Build initial PDF
    doc.build(elements)

    # Process PDF to include only the first page
    reader = PdfReader(temp_output)
    writer = PdfWriter()
    writer.add_page(reader.pages[0])

    # Save final PDF
    with open(output_file, "wb") as f:
        writer.write(f)
    print(f"✅ Resume generated: {output_file}")

if __name__ == "__main__":
    content = load_content("output.yaml")
    build_pdf(content, "Karthikeyan_Baskaran_Resume.pdf")