# router/users.py

from fastapi import APIRouter, Request, Response
import logging
import util

router = APIRouter()

logger = logging.getLogger("daily")


class HashTable:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.table = [[] for _ in range(capacity)]

    def hash_func(self, key):
        return hash(key) % self.capacity

    def set(self, key, value):
        hash_key = self.hash_func(key)
        for pair in self.table[hash_key]:
            if pair[0] == key:
                pair[1] = value
                return
        self.table[hash_key].append([key, value])

    def get(self, key):
        hash_key = self.hash_func(key)
        for pair in self.table[hash_key]:
            if pair[0] == key:
                return pair[1]
        raise KeyError(key)

    def delete(self, key):
        hash_key = self.hash_func(key)
        for i, pair in enumerate(self.table[hash_key]):
            if pair[0] == key:
                del self.table[hash_key][i]
                return
        raise KeyError(key)

    def get_all_users(self):
        all_users = []
        for bucket in self.table:
            for pair in bucket:
                all_users.append(pair)
        return all_users


userTable = HashTable()

with open('user.txt') as f:
    lines = f.readlines()
    for line in lines:
        username, password = line.strip().split(':')
        userTable.set(username, password)


@router.get("/register")
def register(username: str, password: str):
    userTable.set(username, password)
    with open('user.txt', 'a') as f:
        f.write(f'{username}:{password}\n')
    logger.info(f"Register success: {username}")
    return {"message": "Register success"}


@router.get("/login")
def login(username: str, password: str, response: Response):
    try:
        if userTable.get(username) == password:
            response.set_cookie(key="user", value=username, max_age=86400)
            logger.info(f"Login success: {username}")
            return {"message": "Login success"}
        else:
            return {"message": "Login failed"}
    except KeyError:
        return {"message": "Login failed"}


@router.get("/logout")
def logout(request: Request, response: Response):
    username = request.cookies.get("user")
    response.delete_cookie(key="user")
    logger.info(f"Logout success: {username}")
    return {"message": "Logout success"}


@router.get("/add_account")
def add_account(username: str, password: str):
    userTable.set(username, password)
    with open('user.txt', 'a') as f:
        f.write(f'{username}:{password}\n')
    logger.info(f"Add success: {username}")
    return {"message": "Add success"}


@router.get("/delete_account")
def delete_account(request: Request, username: str):
    util.getUser(request)
    userTable.delete(username)
    with open('user.txt', 'r') as f:
        lines = f.readlines()
    with open('user.txt', 'w') as f:
        for line in lines:
            if line.split(':')[0] != username:
                f.write(line)
    logger.info(f"Delete success: {username}")
    return {"message": "Delete success"}


@router.get("/get_all_user")
def get_users(request: Request):
    util.getUser(request)
    users = []
    for hash_key in range(userTable.capacity):
        for pair in userTable.table[hash_key]:
            users.append({"username": pair[0], "password": pair[1]})
    logger.info("Get all users")
    return {"users": users}


@router.get("/get_user")
def gets_user(request: Request, username: str):
    util.getUser(request)
    try:
        password = userTable.get(username)
        logger.info(f"Get user: {username}")
        return {"username": username, "password": password}
    except KeyError:
        logger.info(f"Get user failed: {username}")
        return {"message": "Get user failed"}
