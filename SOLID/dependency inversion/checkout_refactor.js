import sqlite3 from "sqlite3";
import nodemailer from "nodemailer";

export class Database {
  constructor(path) {
    this.db = new sqlite3.Database(path);
  }

  async execute(query, params) {
    return new Promise((resolve, reject) => {
      this.db.run(query, params, function (err) {
        if (err) reject(err);
        else resolve({ id: this.lastID });
      });
    });
  }
}


export class EmailService {
  constructor({ host, port, from }) {
    this.from = from;
    this.transporter = nodemailer.createTransport({
      host,
      port,
    });
  }

  async sendMail({ to, subject, text }) {
    return this.transporter.sendMail({ from: this.from, to, subject, text });
  }
}


export async function checkout(order, db, emailService) {
  const save = await db.execute("INSERT INTO orders(email,total) VALUES(?,?)", [order.email, order.total]);
  await emailService.sendMail({
    to: order.email,
    subject: "Order confirmed",
    text: `Order #${save.id} total=${order.total}`,
  });
  return { orderId: save.id };
}
