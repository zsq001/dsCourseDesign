# router/users.py

from fastapi import APIRouter, Request, Response

router = APIRouter()


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

    return {"message": "Register success"}


@router.get("/login")
def login(username: str, password: str, response: Response):
    try:
        if userTable.get(username) == password:
            response.set_cookie(key="user", value=username, max_age=86400)
            return {"message": "Login success"}
        else:
            return {"message": "Login failed"}
    except KeyError:
        return {"message": "Login failed"}


@router.get("/logout")
def logout(response: Response):
    response.delete_cookie(key="user")
    return {"message": "Logout success"}
