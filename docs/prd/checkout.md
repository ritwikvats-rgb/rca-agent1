# PRD — Checkout v1 (Plain English)

What is this? Users can pay and finish checkout.

Why it matters? Failed/slow checkout loses revenue.

Rules:
- Finish in 5 seconds for 95% users (P95).
- If payment gateway is slow (>5s), retry once.
- Log request_id, user_id, amount on error.

Acceptance:
- A 5s timeout guard exists.
- One retry on timeout.
- Clear error returned to UI and logs contain context.

Implication:
- Without timeout, users get stuck; business loses money.
