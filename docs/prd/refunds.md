# PRD — Refunds v1 (Plain English)

What is this? Refund limits by user tier.

Why it matters? Missing config breaks refunds.

Rules:
- Must have both tiers: standard and premium.
- If a tier is missing, do NOT crash; return a friendly error and log it.

Acceptance:
- No KeyError when reading limits.
- Missing tier → clear error + log.

How:
- Use LIMITS.get(tier) with a default, and validate config at startup/CI.
