# A third repo for realism.
class LoginRateLimitError(Exception): 
    pass

def login(username: str, password: str, attempts: int) -> str:
    if attempts > 10: 
        raise LoginRateLimitError('too many attempts')
    return 'OK'
