"""Build PR Markdown with proposed fixes."""
from jinja2 import Environment, FileSystemLoader
from .schema import RCAData


def generate_pr_draft(rca_data: RCAData, output_dir: str = "out") -> dict:
    """Generate PR draft markdown."""
    env = Environment(
        loader=FileSystemLoader('docs/templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    template = env.get_template('pr_draft.md.j2')
    
    # Generate risks based on the fixes
    risks = generate_risks(rca_data)
    
    content = template.render(
        incident=rca_data.incident,
        summary=rca_data.summary,
        diffs=rca_data.diffs,
        risks=risks,
        validations=rca_data.validations
    )
    
    # Save to file
    incident_id = rca_data.incident.id
    output_path = f"{output_dir}/{incident_id}_pr_draft.md"
    
    import os
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    return {
        'path': output_path,
        'content': content
    }


def generate_risks(rca_data: RCAData) -> list:
    """Generate risk assessment for the proposed fixes."""
    risks = []
    
    # Analyze each diff for potential risks
    for diff in rca_data.diffs:
        if "timeout" in diff.lower():
            risks.extend([
                "Timeout changes may affect user experience",
                "Retry logic could increase load on payment gateway",
                "Need to verify timeout values don't break other integrations"
            ])
        
        if "limits.get" in diff.lower():
            risks.extend([
                "Default behavior change may affect existing users",
                "Need to ensure all tier configurations are validated",
                "Error messages should be consistent across services"
            ])
    
    # Generic risks if no specific ones found
    if not risks:
        risks = [
            "Changes may have unintended side effects",
            "Requires thorough testing before deployment",
            "Monitor error rates after deployment"
        ]
    
    return risks


def generate_pr_summary(rca_data: RCAData) -> str:
    """Generate a concise summary for the PR."""
    incident = rca_data.incident
    observations = rca_data.observations
    
    summary_parts = [
        f"Fixes {incident.title.lower()} ({incident.id})"
    ]
    
    # Add key observations
    business_logic_issues = [obs for obs in observations if obs.kind == "business_logic"]
    if business_logic_issues:
        summary_parts.append("Addresses PRD compliance violations:")
        for obs in business_logic_issues:
            summary_parts.append(f"- {obs.note}")
    
    code_quality_issues = [obs for obs in observations if obs.kind == "code_quality"]
    if code_quality_issues:
        summary_parts.append("Improves code quality:")
        for obs in code_quality_issues:
            summary_parts.append(f"- {obs.note}")
    
    return "\n".join(summary_parts)
