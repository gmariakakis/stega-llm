import { decodeSecretMessage } from './encoder.js';

export async function decodeStegoText(model, tokenizer, coverText) {
  const tokens = (await tokenizer.encode(coverText)).inputIds;
  const bits = tokens.map(id => String(id % 2)).join('');
  return decodeSecretMessage(bits);
}
