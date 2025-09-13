# Fixed: Safe dict access to prevent KeyError
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
