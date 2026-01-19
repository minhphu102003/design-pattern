export class AIProvider {
  async chat(prompt, opts) { throw new Error("Not implemented"); }
  async *streamChat(prompt, opts) { throw new Error("Not implemented"); }

  async embed(texts) { throw new Error("Not implemented"); }
  async moderate(text) { throw new Error("Not implemented"); }

  async chatWithTools(prompt, tools, opts) { throw new Error("Not implemented"); }
  async image(prompt) { throw new Error("Not implemented"); }
}

// Client 1: RAG Retriever chỉ cần embed()
export async function buildIndex(provider, docs) {
  const vectors = await provider.embed(docs);      
  return vectors.length;
}

// Client 2: Chat UI chỉ cần streamChat()
export async function streamAnswer(provider, prompt) {
  let out = "";
  for await (const chunk of provider.streamChat(prompt)) out += chunk;
  return out;
}

// Client 3: Safety filter chỉ cần moderate()
export async function checkSafety(provider, text) {
  const result = await provider.moderate(text);
  return result.allowed;
}
