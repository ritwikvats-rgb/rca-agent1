"""Command line tool with subcommands to run the whole flow."""
import argparse
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from .loaders import load_incident
from .correlate import get_top_candidate
from .scoring import score_candidates, format_candidate_report
from .analyze import (
    analyze_code, compute_tat, generate_five_whys, 
    generate_candidate_fixes, get_owners, generate_validations, generate_prevention
)
from .schema import RCAData
from .rca_writer import export_rca_documents, export_final_rca_documents
from .pr_draft import generate_pr_draft
from .linear_client import create_ticket_from_rca
from .gitutils import setup_git_history, apply_fix_commit
from .comparison_doc import generate_comparison_doc
from .finalizer import finalize_rca_data, update_incident_resolved_time

console = Console()


def cmd_init(args):
    """Initialize git repository and setup."""
    console.print("[bold blue]Initializing RCA Agent...[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Setting up git repository...", total=None)
        
        commits = setup_git_history()
        
        progress.update(task, description="Git repository initialized")
    
    console.print(f"✅ Git repository initialized")
    console.print(f"📝 Baseline commit: {commits['baseline'][:8]}")
    console.print(f"🐛 Bug commit: {commits['bug'][:8]}")
    console.print(f"🏷️  Release tag: 2025.09.13")


def cmd_triage(args):
    """Triage incident and show candidate analysis."""
    console.print(f"[bold blue]Triaging incident: {args.incident_file}[/bold blue]")
    
    # Load incident
    incident = load_incident(args.incident_file)
    
    # Score candidates
    candidates = score_candidates(incident)
    
    # Display results
    console.print(f"\n[bold green]Incident: {incident.id}[/bold green]")
    console.print(f"Title: {incident.title}")
    console.print(f"Service: {incident.service}")
    console.print(f"Error: {incident.error_message}")
    
    # Show candidate analysis
    console.print(f"\n[bold yellow]Candidate Analysis:[/bold yellow]")
    
    if candidates:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Repository", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Score", justify="right", style="bold")
        table.add_column("Reasons", style="dim")
        
        for i, candidate in enumerate(candidates[:5], 1):
            reasons = "; ".join(candidate.reasons[:2])  # Show first 2 reasons
            if len(candidate.reasons) > 2:
                reasons += f" (+{len(candidate.reasons)-2} more)"
            
            table.add_row(
                str(i),
                candidate.repo,
                candidate.file,
                str(candidate.score),
                reasons
            )
        
        console.print(table)
        
        # Show top candidate
        top = candidates[0]
        console.print(f"\n[bold green]🎯 Top Suspect:[/bold green] {top.repo}/{top.file} (Score: {top.score})")
    else:
        console.print("❌ No candidates found")


def cmd_rca(args):
    """Generate RCA document."""
    console.print(f"[bold blue]Generating RCA for: {args.incident_file}[/bold blue]")
    
    # Load incident
    incident = load_incident(args.incident_file)
    
    # Get top candidate
    suspect = get_top_candidate(incident)
    
    # Analyze code
    observations = analyze_code(incident, suspect)
    
    # Generate analysis components
    whys = generate_five_whys(incident, suspect, observations)
    diffs = generate_candidate_fixes(incident, suspect, observations)
    validations = generate_validations(incident, observations)
    prevention = generate_prevention(incident, observations)
    owners = get_owners(incident)
    tat = compute_tat(incident)
    
    # Create RCA data
    rca_data = RCAData(
        incident=incident,
        suspect=suspect,
        summary=f"Analysis of {incident.title} - {incident.error_message}",
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
        tat=tat,
        impact=incident.impact,
        whys=whys,
        observations=observations,
        diffs=diffs,
        validations=validations,
        prevention=prevention,
        owners=owners
    )
    
    if args.initial:
        # Generate initial RCA
        result = export_rca_documents(rca_data)
        console.print(f"✅ Initial RCA generated:")
        console.print(f"📄 Markdown: {result['markdown']}")
        console.print(f"📄 PDF: {result['pdf']}")
        
    elif args.final and args.fix_commit:
        # Generate final RCA
        fix_info = finalize_rca_data(rca_data, args.fix_commit)
        
        result = export_final_rca_documents(
            rca_data, 
            fix_info['fix_commit'], 
            fix_info['files_changed'], 
            fix_info['fix_summary']
        )
        
        console.print(f"✅ Final RCA generated:")
        console.print(f"📄 Markdown: {result['markdown']}")
        console.print(f"📄 PDF: {result['pdf']}")
        
        # Update incident as resolved
        update_incident_resolved_time(args.incident_file)
        
    else:
        console.print("❌ Please specify --initial or --final with --fix-commit")


def cmd_draft_pr(args):
    """Generate PR draft."""
    console.print(f"[bold blue]Generating PR draft for: {args.incident_file}[/bold blue]")
    
    # Load incident and generate RCA data (simplified)
    incident = load_incident(args.incident_file)
    suspect = get_top_candidate(incident)
    observations = analyze_code(incident, suspect)
    diffs = generate_candidate_fixes(incident, suspect, observations)
    validations = generate_validations(incident, observations)
    
    rca_data = RCAData(
        incident=incident,
        suspect=suspect,
        summary=f"Fix for {incident.title}",
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
        tat=compute_tat(incident),
        impact=incident.impact,
        whys=[],
        observations=observations,
        diffs=diffs,
        validations=validations,
        prevention=[],
        owners=get_owners(incident)
    )
    
    result = generate_pr_draft(rca_data)
    console.print(f"✅ PR draft generated: {result['path']}")


def cmd_ticket(args):
    """Create Linear ticket."""
    console.print(f"[bold blue]Creating ticket for: {args.incident_file}[/bold blue]")
    
    # Load incident and generate RCA data (simplified)
    incident = load_incident(args.incident_file)
    suspect = get_top_candidate(incident)
    observations = analyze_code(incident, suspect)
    
    rca_data = RCAData(
        incident=incident,
        suspect=suspect,
        summary=f"RCA for {incident.title}",
        created_at=incident.created_at,
        resolved_at=incident.resolved_at,
        tat=compute_tat(incident),
        impact=incident.impact,
        whys=[],
        observations=observations,
        diffs=[],
        validations=[],
        prevention=[],
        owners=get_owners(incident)
    )
    
    result = create_ticket_from_rca(incident.id, rca_data, args.team)
    
    if result['success']:
        console.print(f"✅ {result['message']}")
        if result['type'] == 'mock':
            console.print(f"📁 Saved to: {result['file_path']}")
    else:
        console.print(f"❌ Failed to create ticket: {result['error']}")


def cmd_apply_fix(args):
    """Apply fixes and create fix commit."""
    console.print(f"[bold blue]Applying fixes for: {args.incident_file}[/bold blue]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Applying fixes...", total=None)
        
        fix_commit = apply_fix_commit()
        
        progress.update(task, description="Fixes applied and committed")
    
    console.print(f"✅ Fixes applied and committed")
    console.print(f"🔧 Fix commit: {fix_commit[:8]}")
    console.print(fix_commit)  # Print full hash for use in final RCA


def cmd_compare(args):
    """Generate comparison document."""
    console.print(f"[bold blue]Generating comparison for: {args.incident_file}[/bold blue]")
    
    # Load incident
    incident = load_incident(args.incident_file)
    suspect = get_top_candidate(incident)
    
    # Generate comparison (using a dummy fix commit for demo)
    result = generate_comparison_doc(
        incident.id, 
        suspect.repo, 
        suspect.file, 
        "fix_commit_hash"
    )
    
    console.print(f"✅ Comparison document generated: {result['path']}")


def cmd_demo(args):
    """Run complete demo workflow."""
    console.print("[bold green]🚀 Running complete RCA Agent demo...[/bold green]")
    
    incident_file = args.incident_file
    
    # Step 1: Initialize
    console.print("\n[bold blue]Step 1: Initialize[/bold blue]")
    cmd_init(argparse.Namespace())
    
    # Step 2: Triage
    console.print("\n[bold blue]Step 2: Triage[/bold blue]")
    cmd_triage(argparse.Namespace(incident_file=incident_file))
    
    # Step 3: Initial RCA
    console.print("\n[bold blue]Step 3: Initial RCA[/bold blue]")
    cmd_rca(argparse.Namespace(incident_file=incident_file, initial=True, final=False, fix_commit=None))
    
    # Step 4: PR Draft
    console.print("\n[bold blue]Step 4: PR Draft[/bold blue]")
    cmd_draft_pr(argparse.Namespace(incident_file=incident_file))
    
    # Step 5: Ticket
    console.print("\n[bold blue]Step 5: Create Ticket[/bold blue]")
    cmd_ticket(argparse.Namespace(incident_file=incident_file, team="FTS"))
    
    # Step 6: Apply Fix
    console.print("\n[bold blue]Step 6: Apply Fix[/bold blue]")
    fix_result = cmd_apply_fix(argparse.Namespace(incident_file=incident_file))
    
    # Get the fix commit hash (in real implementation, this would be returned)
    from .gitutils import get_current_commit_hash
    fix_commit = get_current_commit_hash()
    
    # Step 7: Final RCA
    console.print("\n[bold blue]Step 7: Final RCA[/bold blue]")
    cmd_rca(argparse.Namespace(incident_file=incident_file, initial=False, final=True, fix_commit=fix_commit))
    
    # Step 8: Comparison
    console.print("\n[bold blue]Step 8: Comparison[/bold blue]")
    cmd_compare(argparse.Namespace(incident_file=incident_file))
    
    console.print("\n[bold green]🎉 Demo completed! Check the 'out/' directory for generated documents.[/bold green]")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="RCA Agent - Root Cause Analysis Automation")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize git repository')
    parser_init.set_defaults(func=cmd_init)
    
    # Triage command
    parser_triage = subparsers.add_parser('triage', help='Triage incident and show candidates')
    parser_triage.add_argument('incident_file', help='Path to incident JSON file')
    parser_triage.set_defaults(func=cmd_triage)
    
    # RCA command
    parser_rca = subparsers.add_parser('rca', help='Generate RCA document')
    parser_rca.add_argument('incident_file', help='Path to incident JSON file')
    parser_rca.add_argument('--initial', action='store_true', help='Generate initial RCA')
    parser_rca.add_argument('--final', action='store_true', help='Generate final RCA')
    parser_rca.add_argument('--fix-commit', help='Fix commit hash for final RCA')
    parser_rca.set_defaults(func=cmd_rca)
    
    # PR draft command
    parser_pr = subparsers.add_parser('draft-pr', help='Generate PR draft')
    parser_pr.add_argument('incident_file', help='Path to incident JSON file')
    parser_pr.set_defaults(func=cmd_draft_pr)
    
    # Ticket command
    parser_ticket = subparsers.add_parser('ticket', help='Create Linear ticket')
    parser_ticket.add_argument('incident_file', help='Path to incident JSON file')
    parser_ticket.add_argument('--team', default='FTS', help='Linear team key')
    parser_ticket.set_defaults(func=cmd_ticket)
    
    # Apply fix command
    parser_fix = subparsers.add_parser('apply-fix', help='Apply fixes and create commit')
    parser_fix.add_argument('incident_file', help='Path to incident JSON file')
    parser_fix.set_defaults(func=cmd_apply_fix)
    
    # Compare command
    parser_compare = subparsers.add_parser('compare', help='Generate comparison document')
    parser_compare.add_argument('incident_file', help='Path to incident JSON file')
    parser_compare.set_defaults(func=cmd_compare)
    
    # Demo command
    parser_demo = subparsers.add_parser('demo', help='Run complete demo workflow')
    parser_demo.add_argument('incident_file', help='Path to incident JSON file')
    parser_demo.set_defaults(func=cmd_demo)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
