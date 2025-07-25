import { encodeSecretMessage, decodeSecretMessage } from './encoder.js';

export async function generateStegoText(model, tokenizer, prompt, secret, maxTokens = null) {
  const secretBits = encodeSecretMessage(secret);
  const nBits = secretBits.length;
  if (maxTokens === null) {
    maxTokens = nBits;
  }

  let tokens = (await tokenizer.encode(prompt)).inputIds;
  const generated = [];
  const vocabSize = model.config.vocab_size;

  for (let i = 0; i < Math.min(nBits, maxTokens); ++i) {
    const bitVal = Number(secretBits[i]);

    const out = await model.forward({ input_ids: tokens });
    const lastLogits = out.logits.slice([0, tokens.length - 1, 0], [1, 1, vocabSize]).squeeze(0).squeeze(0);

    let nextId = 0;
    let best = -Infinity;
    for (let id = 0; id < vocabSize; ++id) {
      if (id % 2 !== bitVal) continue;
      const val = lastLogits[id];
      if (val > best) {
        best = val;
        nextId = id;
      }
    }

    tokens = [...tokens, nextId];
    generated.push(nextId);
  }

  const coverText = await tokenizer.decode(generated, { skipSpecialTokens: true });
  const recoveredBits = generated.map(id => String(id % 2)).join('');
  const recoveredSecret = decodeSecretMessage(recoveredBits);
  return [coverText, recoveredSecret];
}
