import hmac

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = [
    User(1, 'user1', 'user1'),
    User(2, 'user2', 'user2'),
    User(3, 'user3', 'user3')
]

username_table = {user.username: user for user in users}
userid_table = {user.id: user for user in users}

def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)