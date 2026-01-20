// Singleton Pattern - Practice Exercise (JavaScript)
// 
// Bài tập: Hãy implement một Logger Singleton
//
// Yêu cầu:
// 1. Class Logger chỉ có duy nhất 1 instance
// 2. Có method log(message) để ghi log
// 3. Có method getLogCount() để trả về số lần log được gọi
//
// Hướng dẫn:
// - Sử dụng constructor để kiểm soát instance
// - Đếm số lần log được gọi bằng biến logCount
//
// Kiểm tra:
// const logger1 = new Logger();
// const logger2 = new Logger();
// logger1.log("Hello");
// logger2.log("World");
// console.log(logger1.getLogCount());  // Output: 2
// console.log(logger1 === logger2);    // Output: true

class Logger {
    constructor() {
        if(Logger.instance){
            return Logger.instance;
        }
        Logger.instance = this;
        this.logCount = 0;
    }
    
    log(message) {
        this.logCount += 1;
        console.log(message);
    }
    
    getLogCount() {
        return this.logCount;
    }
}

// Test your code here
if (require.main === module) {
    const logger1 = new Logger();
    const logger2 = new Logger();
    
    logger1.log("Hello");
    logger2.log("World");
    
    console.log(`Log count: ${logger1.getLogCount()}`);  // Should be 2
    console.log(`Same instance? ${logger1 === logger2}`); // Should be true
}

module.exports = Logger;
