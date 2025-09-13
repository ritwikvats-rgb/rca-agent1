"""Apply scoring formula and sort candidates."""
from typing import List
from .schema import Incident, Candidate
from .correlate import correlate_incident


def score_candidates(incident: Incident) -> List[Candidate]:
    """Score and rank candidates using the scoring system."""
    candidates = correlate_incident(incident)
    
    # Additional scoring logic can be added here
    # For now, the correlation logic already handles scoring
    
    # Sort by score (highest first)
    candidates.sort(key=lambda c: c.score, reverse=True)
    
    return candidates


def get_scoring_explanation() -> str:
    """Return explanation of the scoring system."""
    return """
Scoring System:
- +3 points: Endpoint match (API route maps to specific file)
- +2 points: Job/workflow match (background job maps to handler)
- +2 points: Error signature match (error type maps to known file)
- +1 point: Mentioned in logs (request ID found in log traces)
- +1 point: Changed in recent release (file modified in version)
- +1 point: Service mapping (base score for service ownership)

The highest-scoring candidate is selected as the primary suspect.
Multiple evidence sources can contribute to the same candidate's score.
"""


def format_candidate_report(candidates: List[Candidate]) -> str:
    """Format candidates into a readable report."""
    if not candidates:
        return "No candidates found."
    
    report = "Candidate Analysis:\n\n"
    
    for i, candidate in enumerate(candidates[:5], 1):  # Top 5
        report += f"{i}. {candidate.repo}/{candidate.file} (Score: {candidate.score})\n"
        for reason in candidate.reasons:
            report += f"   - {reason}\n"
        report += "\n"
    
    if len(candidates) > 5:
        report += f"... and {len(candidates) - 5} more candidates\n"
    
    return report
