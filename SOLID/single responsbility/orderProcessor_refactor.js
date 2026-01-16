// Refactor to adhere to single responsibility principle

class Email {
  constructor(customerEmail, emailClient) {
    this.customerEmail = customerEmail;
    this.emailClient = emailClient;
  }

  validate() {
    if (!this.customerEmail) throw new Error("Missing customerEmail");
  }

  async send(order) {
    this.validate();
    const orderId = order?.id ?? "N/A";
    const total = order?.total ?? 0;
    await this.emailClient.send({
      to: this.customerEmail,
      subject: "Your order confirmation",
      text: `Order ${orderId} total: ${total}`,
    });
  }
}


class Database {
  constructor(db) {
    this.db = db;
  }

  async insert(order) {
    return this.db.orders.insert(order);
  }
}

class Logger {
  constructor(logger) {
    this.logger = logger;
  }

  info(message){
    this.logger.info(message);
  }
}

class PricingSerivce{
  constructor(){}

  calculator(order){
    const subtotal = order.items.reduce((sum, item) => {
      s + item.qty + item.price
    })
    const discount = order.coupon === "SAVE10" ? subtotal * 0.1 : 0;
    const total = Math.max(0, subtotal - discount);
    return { ...order, subtotal, discount, total };
  }
}

class OrderProcessor {
  constructor(email, db, logger, pricingService) {
    this.email = email;
    this.db = db;
    this.logger = logger;
    this.pricingService = pricingService
  }

  async process(order) {
    try{
      this.email.validate();
      const orderWithPrices = this.pricingService.calculator(order);
      const saved = await this.db.insert(orderWithPrices);
      await this.email.send(saved);
      this.logger.info("order_processed", { orderId: saved.id, total: saved.total });
      return { orderId: saved.id, total: saved.total };
    } catch (error) {
      this.logger.error("order_processing_failed", { error });
      throw error;
    }
  }
}
