# PRD — Authentication v1 (Plain English)
What is this? Secure user login with rate limiting protection.
Why it matters? Prevents brute force attacks and protects user accounts.
Rules:
- Maximum 5 login attempts per IP per 15 minutes.
- After 5 failed attempts, block IP for 30 minutes.
- Log all failed attempts with IP, timestamp, and user context.
- Legitimate users should not be affected by rate limiting.
Acceptance:
- Rate limiting triggers after 5 attempts.
- Blocked IPs cannot login for 30 minutes.
- Clear error messages for rate limited users.
- Monitoring alerts on high failure rates.
Implication:
- Without proper rate limiting, accounts vulnerable to brute force attacks.
- Too aggressive rate limiting blocks legitimate users.
