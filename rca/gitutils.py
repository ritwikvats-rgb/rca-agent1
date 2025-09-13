"""Create local git repo, baseline commit, bug commit, tag release, apply fix commit."""
import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Tuple


def init_git_repo(repo_path: str = ".") -> bool:
    """Initialize git repository if not already initialized."""
    try:
        # Check if already a git repo
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=repo_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return True  # Already a git repo
        
        # Initialize new repo
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.name", "RCA Agent"], cwd=repo_path, check=True)
        subprocess.run(["git", "config", "user.email", "rca@example.com"], cwd=repo_path, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def create_baseline_commit(repo_path: str = ".") -> str:
    """Create baseline commit with working code."""
    try:
        # Stage all files
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        
        # Create baseline commit
        subprocess.run(
            ["git", "commit", "-m", "Initial baseline - working code"],
            cwd=repo_path,
            check=True
        )
        
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "baseline_commit_hash"


def create_bug_commit(repo_path: str = ".") -> str:
    """Create commit that introduces the bug (current state)."""
    try:
        # The current state already has the bug, so just commit it
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        
        subprocess.run(
            ["git", "commit", "-m", "Bug: Add timeout issue and unsafe dict access"],
            cwd=repo_path,
            check=True
        )
        
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "bug_commit_hash"


def create_release_tag(tag_name: str, repo_path: str = ".") -> bool:
    """Create a release tag."""
    try:
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", f"Release {tag_name}"],
            cwd=repo_path,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def apply_fix_commit(repo_path: str = ".") -> str:
    """Apply fixes and create fix commit."""
    try:
        # Apply fixes to checkout.ts
        checkout_file = Path(repo_path) / "repos" / "repo-orders" / "src" / "orders" / "checkout.ts"
        if checkout_file.exists():
            fixed_checkout = """// Fixed: Added timeout guard and retry logic
export class CheckoutTimeoutError extends Error {}

async function fakePaymentCall(ms: number): Promise<string> { 
  return new Promise(res => setTimeout(res, ms)); 
}

export async function checkout(amount: number): Promise<string> {
  const started = Date.now();
  
  try {
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
  }
  
  if (Date.now() - started > 5000) {
    throw new CheckoutTimeoutError('payment gateway exceeded 5s');
  }
  return 'OK';
}
"""
            with open(checkout_file, 'w') as f:
                f.write(fixed_checkout)
        
        # Apply fixes to limits.py
        limits_file = Path(repo_path) / "repos" / "repo-payments" / "service" / "payment" / "limits.py"
        if limits_file.exists():
            fixed_limits = """# Fixed: Added missing 'premium' tier
LIMITS = {
    'standard': {'max': 1000},
    'premium': {'max': 5000}  # Added missing tier
}
"""
            with open(limits_file, 'w') as f:
                f.write(fixed_limits)
        
        # Apply fixes to refund.py
        refund_file = Path(repo_path) / "repos" / "repo-payments" / "service" / "payment" / "handlers" / "refund.py"
        if refund_file.exists():
            fixed_refund = """# Fixed: Safe dict access to prevent KeyError
class RefundLimitExceededError(Exception): 
    pass

from .. import limits

def refund_handler(user_tier: str, amount: float) -> str:
    bucket = limits.LIMITS.get(user_tier)
    if not bucket:
        raise RefundLimitExceededError(f'Unknown tier: {user_tier}')
    
    if amount > bucket['max']:
        raise RefundLimitExceededError('limit exceeded')
    return 'OK'
"""
            with open(refund_file, 'w') as f:
                f.write(fixed_refund)
        
        # Stage and commit fixes
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)
        subprocess.run(
            ["git", "commit", "-m", "Fix: Add timeout guard, retry logic, and safe dict access"],
            cwd=repo_path,
            check=True
        )
        
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "fix_commit_hash"


def update_releases_csv_with_commits(base_commit: str, bug_commit: str, repo_path: str = ".") -> None:
    """Update releases.csv with actual commit hashes."""
    try:
        releases_file = Path(repo_path) / "data" / "releases.csv"
        if releases_file.exists():
            content = releases_file.read_text()
            content = content.replace("{BASE_COMMIT}", base_commit[:8])
            content = content.replace("{BUG_COMMIT}", bug_commit[:8])
            releases_file.write_text(content)
    except Exception as e:
        print(f"Warning: Could not update releases.csv: {e}")


def setup_git_history(repo_path: str = ".") -> Dict[str, str]:
    """Set up complete git history for the demo."""
    commits = {}
    
    # Initialize repo
    if not init_git_repo(repo_path):
        print("Warning: Could not initialize git repo")
        return {
            'baseline': 'baseline_commit_hash',
            'bug': 'bug_commit_hash',
            'fix': 'fix_commit_hash'
        }
    
    # Create baseline commit
    commits['baseline'] = create_baseline_commit(repo_path)
    
    # Create bug commit (current state)
    commits['bug'] = create_bug_commit(repo_path)
    
    # Create release tag
    create_release_tag("2025.09.13", repo_path)
    
    # Update releases.csv with actual commit hashes
    update_releases_csv_with_commits(commits['baseline'], commits['bug'], repo_path)
    
    return commits


def get_git_log(repo_path: str = ".", max_commits: int = 10) -> str:
    """Get git log for demonstration."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{max_commits}"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "Git log not available"


def get_current_commit_hash(repo_path: str = ".") -> str:
    """Get current commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown_commit"
