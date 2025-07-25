export const charSet = " abcdefghijklmnopqrstuvwxyz.,!?";

export const charToBin = {};
export const binToChar = {};
for (let i = 0; i < charSet.length; ++i) {
  const ch = charSet[i];
  const code = i.toString(2).padStart(5, "0");
  charToBin[ch] = code;
  binToChar[code] = ch;
}

export const upperMarker = "11111";

export function encodeSecretMessage(text) {
  const bits = [];
  for (const ch of text) {
    const lower = ch.toLowerCase();
    if (lower in charToBin) {
      if (ch !== lower) bits.push(upperMarker);
      bits.push(charToBin[lower]);
    }
  }
  return bits.join("");
}

export function decodeSecretMessage(bitStr) {
  const chars = [];
  let i = 0;
  let uppercaseNext = false;
  while (i + 5 <= bitStr.length) {
    const chunk = bitStr.slice(i, i + 5);
    i += 5;
    if (chunk === upperMarker) {
      uppercaseNext = true;
      continue;
    }
    const ch = binToChar[chunk];
    if (!ch) continue;
    chars.push(uppercaseNext ? ch.toUpperCase() : ch);
    uppercaseNext = false;
  }
  return chars.join("");
}
