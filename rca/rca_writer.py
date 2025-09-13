"""Render Jinja templates into Markdown and export PDFs."""
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from .schema import RCAData


def setup_jinja_env() -> Environment:
    """Set up Jinja2 environment."""
    return Environment(
        loader=FileSystemLoader('docs/templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )


def render_initial_rca(rca_data: RCAData) -> str:
    """Render initial RCA markdown."""
    env = setup_jinja_env()
    template = env.get_template('rca_initial.md.j2')
    
    return template.render(
        incident=rca_data.incident,
        summary=rca_data.summary,
        created_at=rca_data.created_at,
        resolved_at=rca_data.resolved_at,
        tat=rca_data.tat,
        impact=rca_data.impact,
        suspect=rca_data.suspect,
        whys=rca_data.whys,
        observations=rca_data.observations,
        diffs=rca_data.diffs,
        validations=rca_data.validations,
        prevention=rca_data.prevention,
        owners=rca_data.owners
    )


def render_final_rca(rca_data: RCAData, fix_commit: str, files_changed: str, fix_summary: str) -> str:
    """Render final RCA markdown."""
    env = setup_jinja_env()
    template = env.get_template('rca_final.md.j2')
    
    return template.render(
        incident=rca_data.incident,
        fix_commit=fix_commit,
        files_changed=files_changed,
        fix_summary=fix_summary,
        created_at=rca_data.created_at,
        resolved_at=rca_data.resolved_at,
        tat=rca_data.tat,
        validations=rca_data.validations,
        prevention=rca_data.prevention,
        owners=rca_data.owners
    )


def save_markdown(content: str, output_path: str) -> None:
    """Save markdown content to file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)


def markdown_to_pdf(markdown_content: str, pdf_path: str) -> None:
    """Convert markdown to PDF using reportlab."""
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        textColor='#2c3e50'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=8,
        textColor='#34495e'
    )
    
    # Parse markdown content (simple implementation)
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue
            
        if line.startswith('# '):
            # Main title
            title = line[2:].strip()
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))
        elif line.startswith('## '):
            # Section heading
            heading = line[3:].strip()
            story.append(Paragraph(heading, heading_style))
            story.append(Spacer(1, 8))
        elif line.startswith('- '):
            # Bullet point
            bullet = line[2:].strip()
            story.append(Paragraph(f"• {bullet}", styles['Normal']))
        elif line.startswith('**') and line.endswith('**'):
            # Bold text
            bold_text = line[2:-2]
            story.append(Paragraph(f"<b>{bold_text}</b>", styles['Normal']))
        else:
            # Regular paragraph
            if line:
                story.append(Paragraph(line, styles['Normal']))
    
    # Build PDF
    doc.build(story)


def export_rca_documents(rca_data: RCAData, output_dir: str = "out") -> dict:
    """Export RCA documents in multiple formats."""
    incident_id = rca_data.incident.id
    
    # Render markdown
    markdown_content = render_initial_rca(rca_data)
    
    # File paths
    md_path = f"{output_dir}/{incident_id}_initial_rca.md"
    pdf_path = f"{output_dir}/{incident_id}_initial_rca.pdf"
    
    # Save files
    save_markdown(markdown_content, md_path)
    markdown_to_pdf(markdown_content, pdf_path)
    
    return {
        'markdown': md_path,
        'pdf': pdf_path,
        'content': markdown_content
    }


def export_final_rca_documents(rca_data: RCAData, fix_commit: str, files_changed: str, 
                              fix_summary: str, output_dir: str = "out") -> dict:
    """Export final RCA documents."""
    incident_id = rca_data.incident.id
    
    # Render markdown
    markdown_content = render_final_rca(rca_data, fix_commit, files_changed, fix_summary)
    
    # File paths
    md_path = f"{output_dir}/{incident_id}_final_rca.md"
    pdf_path = f"{output_dir}/{incident_id}_final_rca.pdf"
    
    # Save files
    save_markdown(markdown_content, md_path)
    markdown_to_pdf(markdown_content, pdf_path)
    
    return {
        'markdown': md_path,
        'pdf': pdf_path,
        'content': markdown_content
    }
