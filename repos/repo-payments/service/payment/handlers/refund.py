# Business-logic bug: uses direct dict index; breaks if tier missing.
class RefundLimitExceededError(Exception): 
    pass

from .. import limits

def refund_handler(user_tier: str, amount: float) -> str:
    bucket = limits.LIMITS[user_tier]  # KeyError if 'premium' missing
    if amount > bucket['max']:
        raise RefundLimitExceededError('limit exceeded')
    return 'OK'
