"""Load PRDs + guidelines, scan suspect file for rule hits, compute TAT."""
import re
from datetime import datetime
from typing import List, Optional
from .schema import Incident, Candidate, Observation
from .loaders import load_guidelines, load_prd_yaml, load_repo_file, load_services


def analyze_code(incident: Incident, suspect: Candidate) -> List[Observation]:
    """Analyze suspect code against PRDs and guidelines."""
    observations = []
    
    # Load guidelines
    guidelines = load_guidelines()
    
    # Load source code
    code = load_repo_file(suspect.repo, suspect.file)
    if not code:
        return observations
    
    # Check each guideline pattern
    for guideline in guidelines:
        pattern = guideline['pattern']
        rule_type = guideline['type']
        explanation = guideline['explanation']
        
        # Check if pattern matches
        if _pattern_matches(pattern, code, incident):
            observations.append(Observation(
                kind=rule_type,
                note=explanation,
                rule=pattern
            ))
    
    return observations


def _pattern_matches(pattern: str, code: str, incident: Incident) -> bool:
    """Check if a pattern matches the code or incident."""
    
    # Special patterns
    if pattern == "gateway exceeded 5s":
        return "gateway exceeded 5s" in incident.error_message
    
    if pattern == "missing_log_context":
        # Check if error handling lacks context logging
        return "throw" in code and not any(field in code for field in ["request_id", "user_id", "amount"])
    
    if pattern == "function_lines_gt_50":
        # Simple heuristic: count lines in functions
        lines = code.split('\n')
        return len(lines) > 50
    
    if pattern == "bare except":
        return re.search(r'except\s*:', code) is not None
    
    # Regex patterns
    try:
        return re.search(pattern, code) is not None
    except re.error:
        return False


def compute_tat(incident: Incident) -> Optional[str]:
    """Compute turnaround time from created_at to resolved_at."""
    if not incident.resolved_at:
        return None
    
    try:
        created = datetime.fromisoformat(incident.created_at.replace('Z', '+00:00'))
        resolved = datetime.fromisoformat(incident.resolved_at.replace('Z', '+00:00'))
        delta = resolved - created
        
        hours = delta.total_seconds() / 3600
        if hours < 1:
            minutes = delta.total_seconds() / 60
            return f"{minutes:.0f} minutes"
        elif hours < 24:
            return f"{hours:.1f} hours"
        else:
            days = hours / 24
            return f"{days:.1f} days"
    except Exception:
        return "Unable to calculate"


def generate_five_whys(incident: Incident, suspect: Candidate, observations: List[Observation]) -> List[str]:
    """Generate 5 Whys analysis."""
    whys = []
    
    # Why 1: What happened?
    whys.append(f"Why did {incident.title.lower()}? {incident.error_message}")
    
    # Why 2: Technical cause
    if observations:
        primary_obs = observations[0]
        whys.append(f"Why did this error occur? {primary_obs.note}")
    else:
        whys.append(f"Why did this error occur? Code in {suspect.file} failed")
    
    # Why 3: Root cause
    if any(obs.kind == "business_logic" for obs in observations):
        whys.append("Why wasn't this prevented? Missing business logic safeguards per PRD requirements")
    else:
        whys.append("Why wasn't this prevented? Code quality issues allowed the bug to persist")
    
    # Why 4: Process gap
    whys.append("Why weren't safeguards in place? Insufficient validation during development/review")
    
    # Why 5: System gap
    whys.append("Why wasn't this caught earlier? Missing automated checks for PRD compliance")
    
    return whys


def generate_candidate_fixes(incident: Incident, suspect: Candidate, observations: List[Observation]) -> List[str]:
    """Generate candidate fix diffs."""
    diffs = []
    
    # Load the suspect code
    code = load_repo_file(suspect.repo, suspect.file)
    if not code:
        return diffs
    
    # Generate fixes based on observations
    for obs in observations:
        if obs.rule == "gateway exceeded 5s":
            diff = """--- a/src/orders/checkout.ts
+++ b/src/orders/checkout.ts
@@ -6,7 +6,15 @@ export async function checkout(amount: number): Promise<string> {
   const started = Date.now();
-  await fakePaymentCall(6000); // simulate a slow gateway (6s)
+  
+  try {
+    await Promise.race([
+      fakePaymentCall(6000),
+      new Promise((_, reject) => setTimeout(() => reject(new CheckoutTimeoutError('5s timeout')), 5000))
+    ]);
+  } catch (error) {
+    if (error instanceof CheckoutTimeoutError) {
+      // Retry once
+      await fakePaymentCall(3000);
+    } else {
+      throw error;
+    }
+  }
+  
   if (Date.now() - started > 5000) {
     throw new CheckoutTimeoutError('payment gateway exceeded 5s');
   }"""
            diffs.append(diff)
        
        elif "LIMITS[" in obs.rule:
            diff = """--- a/service/payment/handlers/refund.py
+++ b/service/payment/handlers/refund.py
@@ -5,7 +5,10 @@ from .. import limits
 
 def refund_handler(user_tier: str, amount: float) -> str:
-    bucket = limits.LIMITS[user_tier]  # KeyError if 'premium' missing
+    bucket = limits.LIMITS.get(user_tier)
+    if not bucket:
+        raise RefundLimitExceededError(f'Unknown tier: {user_tier}')
+    
     if amount > bucket['max']:
         raise RefundLimitExceededError('limit exceeded')
     return 'OK'"""
            diffs.append(diff)
    
    return diffs


def get_owners(incident: Incident) -> str:
    """Get owners for the incident."""
    services = load_services()
    service_info = services.get(incident.service, {})
    return service_info.get('owners', '@unknown')


def generate_validations(incident: Incident, observations: List[Observation]) -> List[str]:
    """Generate validation steps."""
    validations = []
    
    for obs in observations:
        if obs.rule == "gateway exceeded 5s":
            validations.extend([
                "Test checkout with 6s+ gateway delay - should timeout at 5s",
                "Test checkout with 4s gateway delay - should succeed",
                "Test checkout timeout retry - should attempt once",
                "Verify P95 latency stays under 5s in load testing"
            ])
        elif "LIMITS[" in obs.rule:
            validations.extend([
                "Test refund with missing tier config - should return clear error",
                "Test refund with valid tiers - should work normally",
                "Verify no KeyError exceptions in logs",
                "Test startup validation catches missing tier config"
            ])
    
    if not validations:
        validations = [
            "Manual testing of the affected functionality",
            "Review error logs for similar patterns",
            "Load testing to verify performance impact"
        ]
    
    return validations


def generate_prevention(incident: Incident, observations: List[Observation]) -> List[str]:
    """Generate prevention measures."""
    prevention = []
    
    for obs in observations:
        if obs.kind == "business_logic":
            prevention.extend([
                "Add automated PRD compliance checks to CI/CD",
                "Create integration tests for SLA requirements",
                "Add monitoring alerts for timeout violations"
            ])
        elif obs.kind == "code_quality":
            prevention.extend([
                "Add linting rules for code quality patterns",
                "Require code review for error handling",
                "Add static analysis for exception safety"
            ])
    
    if not prevention:
        prevention = [
            "Improve error handling patterns",
            "Add more comprehensive testing",
            "Enhance monitoring and alerting"
        ]
    
    return prevention
