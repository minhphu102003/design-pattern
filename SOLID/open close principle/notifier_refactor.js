// using open close principle

const CHANNELS  = new Map()

export function registerChannel(name, handler) {
  if (CHANNELS.has(name)) throw new Error(`Duplicate channel: ${name}`)
  CHANNELS.set(name, handler)
}

export async function sendNotification({ channel, to, message }, deps) {
  const handler = CHANNELS.get(channel)
  if (!handler) throw new Error("Unknow channel")
    return handler({to, message}, deps)
}

export function unregisterChannel(name) {
  return CHANNELS.delete(name)
}

registerChannel("Email", ({to, message}, deps) => {
  deps.email.send({to, subject: "Notice", text: message})
})

registerChannel("SMS", ({to, message}, deps) => {
  deps.sms.send({to, message})
})

unregisterChannel("Email")

registerChannel("Slack", ({channel, message}, deps) => {
  deps.slack.post({channel, text: message})
})
