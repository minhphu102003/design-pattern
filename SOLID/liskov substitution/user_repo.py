# VIOLATION

class UserRepo:
    def get(self, user_id: int):
        return None

class StrictUserRepo(UserRepo):
    def get(self, user_id: int):
        raise KeyError("user not found")

def show_user_name(repo: UserRepo, user_id: int) -> str:
    user = repo.get(user_id)
    return user["name"] if user else "Guest"


# REFACTOR

class UserRepo:
    def get(self, user_id: int):
        return None

class StrictUserRepo(UserRepo):
    def get(self, user_id: int):
        return {"name": "John Doe"}
    
def show_user_name(repo: UserRepo, user_id: int) -> str:
    user = repo.get(user_id)
    return user["name"] if user else "Guest"

