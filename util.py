from fastapi import Request, HTTPException


def __init__(self):
    return self


def getUser(request: Request):
    user = request.cookies.get("user")
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthenticated")
    if user == 'admin':
        user = 0
    print(user)
    return user
