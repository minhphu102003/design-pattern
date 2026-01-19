import sqlite3 from "sqlite3";
import nodemailer from "nodemailer";

export async function checkout(order) {
  // low-level details nằm trong use-case
  const db = new sqlite3.Database(process.env.DB_PATH || "app.db");
  const transporter = nodemailer.createTransport({
    host: process.env.SMTP_HOST || "localhost",
    port: Number(process.env.SMTP_PORT || 25),
  });

  const saved = await new Promise((resolve, reject) => {
    db.run(
      "INSERT INTO orders(email,total) VALUES(?,?)",
      [order.email, order.total],
      function (err) {
        if (err) reject(err);
        else resolve({ id: this.lastID, ...order });
      }
    );
  });

  await transporter.sendMail({
    from: process.env.EMAIL_FROM || "noreply@example.com",
    to: saved.email,
    subject: "Order confirmed",
    text: `Order #${saved.id} total=${saved.total}`,
  });

  return { orderId: saved.id };
}
