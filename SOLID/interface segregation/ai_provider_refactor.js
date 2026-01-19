export class ChatProvider {
  async chat(prompt) { throw new Error("Not implemented")}
}

export class StreamChatProvider {
  async *streamChat(prompt) { throw new Error("Not implemented")}
}

export class EmbedProvider {
  async embed(texts) { throw new Error("Not implemented")}
}

export class ModerateProvider {
  async moderate(text) { throw new Error("Not implemented")}
}

export class ChatWithToolsProvider {
  async chatWithTools(prompt, tools) { throw new Error("Not implemented")}
}

export class ImageProvider{
  async image(prompt) { throw new Error("Not implemented")}
}

export async function buildIndex(provider, docs) {
  const vectors = await provider.embed(docs);      
  return vectors.length;
}

export async function streamAnswer(provider, prompt) {
  let out = "";
  for await (const chunk of provider.streamChat(prompt)) out += chunk;
  return out;
}

export async function checkSafety(provider, text) {
  return provider.moderate(text);
}
