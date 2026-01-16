// orderProcessor.js
// Example about violate single responsibility principle

export async function processOrder(order, db, emailClient, logger) {
  // 1) Validate
  if (!order?.customerEmail) throw new Error("Missing customerEmail");
  if (!Array.isArray(order.items) || order.items.length === 0) throw new Error("Empty items");

  // 2) Calculate total + discount
  let subtotal = 0;
  for (const item of order.items) {
    if (!item.sku || item.qty <= 0 || item.price < 0) throw new Error("Invalid item");
    subtotal += item.qty * item.price;
  }
  const discount = order.coupon === "SAVE10" ? subtotal * 0.1 : 0;
  const total = Math.max(0, subtotal - discount);

  // 3) Persist
  const saved = await db.orders.insert({
    ...order,
    subtotal,
    discount,
    total,
    status: "PAID",
    createdAt: new Date().toISOString(),
  });

  // 4) Email
  await emailClient.send({
    to: order.customerEmail,
    subject: "Your order confirmation",
    text: `Order ${saved.id} total: ${total}`,
  });

  // 5) Logging/Audit
  logger.info("order_processed", { orderId: saved.id, total });

  return { orderId: saved.id, total };
}
