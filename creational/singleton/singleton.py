# Singleton Pattern in Python
# Mục tiêu: Chỉ có duy nhất 1 instance của class được tạo trong toàn bộ ứng dụng

class Singleton:
    """
    Cách 1: Sử dụng Metaclass (Pythonic)
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.value = None


class Database:
    """
    Ví dụ thực tế: Database connection singleton
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.connection = f"Connected to DB at {id(self)}"
        self._initialized = True
    
    def query(self, sql):
        return f"Executing: {sql} on {self.connection}"


# Test
if __name__ == "__main__":
    db1 = Database()
    db2 = Database()
    
    print(f"db1 ID: {id(db1)}")
    print(f"db2 ID: {id(db2)}")
    print(f"Cùng object? {db1 is db2}")  # True
    print(db1.query("SELECT * FROM users"))
    print(db2.query("SELECT * FROM products"))
