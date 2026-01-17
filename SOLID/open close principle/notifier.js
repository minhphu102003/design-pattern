// notifier.js
export async function sendNotification({ channel, to, message }, deps) {
  switch (channel) {
    case "EMAIL":
      return deps.email.send({ to, subject: "Notice", text: message });
    case "SMS":
      return deps.sms.send({ to, text: message });
    case "SLACK":
      return deps.slack.post({ channel: to, text: message });
    default:
      throw new Error("Unknown channel");
  }
}
