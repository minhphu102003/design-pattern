# Singleton Pattern - Practice Exercise
# 
# Bài tập: Hãy implement một Logger Singleton
#
# Yêu cầu:
# 1. Class Logger chỉ có duy nhất 1 instance
# 2. Có method log(message) để ghi log
# 3. Có method get_log_count() để trả về số lần log được gọi
#
# Hướng dẫn:
# - Sử dụng __new__ để kiểm soát instance
# - Đếm số lần log được gọi bằng biến _log_count
#
# Kiểm tra:
# logger1 = Logger()
# logger2 = Logger()
# logger1.log("Hello")
# logger2.log("World")
# print(logger1.get_log_count())  # Output: 2
# print(logger1 is logger2)        # Output: True

class Logger:
    
    _instance = None
    _log_count = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def log(self, message: str) -> None:
        self._log_count +=1
        print(message)
    
    def get_log_count(self) -> int:
        return self._log_count


# Test your code here
if __name__ == "__main__":
    logger1 = Logger()
    logger2 = Logger()
    
    logger1.log("Hello")
    logger2.log("World")
    
    print(f"Log count: {logger1.get_log_count()}")  # Should be 2
    print(f"Same instance? {logger1 is logger2}")    # Should be True
