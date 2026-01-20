// Singleton Pattern in JavaScript
// Mục tiêu: Chỉ có duy nhất 1 instance của class được tạo trong toàn bộ ứng dụng

// Cách 1: Sử dụng Class với static
class Singleton {
    constructor() {
        if (Singleton.instance) {
            return Singleton.instance;
        }
        Singleton.instance = this;
        this.value = null;
    }
}

// Cách 2: Thực tế - Database connection singleton
class Database {
    constructor() {
        if (Database.instance) {
            return Database.instance;
        }
        
        this.connection = `Connected to DB at ${Date.now()}`;
        Database.instance = this;
    }
    
    query(sql) {
        return `Executing: ${sql} on ${this.connection}`;
    }
}

// Test
const db1 = new Database();
const db2 = new Database();

console.log(`db1 ID: ${db1.constructor.name}`);
console.log(`db2 ID: ${db2.constructor.name}`);
console.log(`Cùng object? ${db1 === db2}`); // true
console.log(db1.query("SELECT * FROM users"));
console.log(db2.query("SELECT * FROM products"));

// Module export
module.exports = Database;
