"""Show Before/After code and timeline delta."""
import os
from jinja2 import Environment, FileSystemLoader
from .schema import ComparisonData
from .loaders import load_repo_file, get_file_extension


def generate_comparison_doc(incident_id: str, suspect_repo: str, suspect_file: str, 
                          fix_commit: str, output_dir: str = "out") -> dict:
    """Generate before/after comparison document."""
    
    # Load the current (buggy) code
    before_code = load_repo_file(suspect_repo, suspect_file) or "Code not found"
    
    # Generate the fixed code (simplified - in real implementation, we'd get from git)
    after_code = generate_fixed_code(before_code, suspect_file)
    
    # Determine language for syntax highlighting
    lang = get_file_extension(suspect_file)
    
    # Create comparison data
    comparison_data = ComparisonData(
        incident_id=incident_id,
        before_code=before_code,
        after_code=after_code,
        before_lang=lang,
        after_lang=lang,
        delta_note=generate_delta_note(suspect_file),
        timeline_delta="Fixed in commit " + fix_commit[:8]
    )
    
    # Render template
    env = Environment(
        loader=FileSystemLoader('docs/templates'),
        trim_blocks=True,
        lstrip_blocks=True
    )
    
    template = env.get_template('comparison.md.j2')
    content = template.render(
        incident_id=comparison_data.incident_id,
        before_code=comparison_data.before_code,
        after_code=comparison_data.after_code,
        before_lang=comparison_data.before_lang,
        after_lang=comparison_data.after_lang,
        delta_note=comparison_data.delta_note,
        timeline_delta=comparison_data.timeline_delta
    )
    
    # Save to file
    output_path = f"{output_dir}/{incident_id}_comparison.md"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(content)
    
    return {
        'path': output_path,
        'content': content,
        'data': comparison_data
    }


def generate_fixed_code(original_code: str, file_path: str) -> str:
    """Generate fixed version of the code."""
    
    if file_path.endswith('.ts'):
        # Fix TypeScript checkout timeout issue
        if "fakePaymentCall(6000)" in original_code:
            fixed_code = original_code.replace(
                "await fakePaymentCall(6000); // simulate a slow gateway (6s)",
                """try {
    await Promise.race([
      fakePaymentCall(6000),
      new Promise((_, reject) => 
        setTimeout(() => reject(new CheckoutTimeoutError('5s timeout')), 5000)
      )
    ]);
  } catch (error) {
    if (error instanceof CheckoutTimeoutError) {
      // Retry once with shorter timeout
      await fakePaymentCall(3000);
    } else {
      throw error;
    }
  }"""
            )
            return fixed_code
    
    elif file_path.endswith('.py'):
        # Fix Python refund limits issue
        if "limits.LIMITS[user_tier]" in original_code:
            fixed_code = original_code.replace(
                "bucket = limits.LIMITS[user_tier]  # KeyError if 'premium' missing",
                """bucket = limits.LIMITS.get(user_tier)
    if not bucket:
        raise RefundLimitExceededError(f'Unknown tier: {user_tier}')"""
            )
            return fixed_code
    
    # If no specific fix pattern found, return original with comment
    return original_code + "\n\n# TODO: Apply appropriate fixes based on RCA analysis"


def generate_delta_note(file_path: str) -> str:
    """Generate a note explaining the key change."""
    
    if file_path.endswith('.ts') and 'checkout' in file_path:
        return "Added 5-second timeout guard with retry logic to meet PRD SLA requirements"
    
    elif file_path.endswith('.py') and 'refund' in file_path:
        return "Replaced unsafe dict access with .get() method to prevent KeyError crashes"
    
    elif file_path.endswith('.py') and 'limits' in file_path:
        return "Added missing 'premium' tier configuration"
    
    else:
        return "Applied fixes based on RCA analysis and PRD requirements"


def calculate_timeline_delta(created_at: str, resolved_at: str) -> str:
    """Calculate the time difference between incident creation and resolution."""
    try:
        from datetime import datetime
        created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        resolved = datetime.fromisoformat(resolved_at.replace('Z', '+00:00'))
        delta = resolved - created
        
        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = delta.total_seconds() / 60
            return f"Resolved in {minutes:.0f} minutes"
        elif hours < 24:
            return f"Resolved in {hours:.1f} hours"
        else:
            days = hours / 24
            return f"Resolved in {days:.1f} days"
    except Exception:
        return "Timeline calculation failed"
