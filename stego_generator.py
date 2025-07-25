# stego_generator.py

import torch
from tqdm.auto import tqdm
from typing import Tuple

from encoder import (
    encode_secret_message,
    decode_secret_message,
    encrypt_message,
    decrypt_message,
    bytes_to_bits,
    bits_to_bytes,
)

def generate_stego_text(
    model,
    tokenizer,
    prompt: str,
    secret: str,
    *,
    encryption_key: bytes | None = None,
    max_tokens: int = None,
    temperature: float = 1.0,
    top_k: int | None = None,
) -> Tuple[str, str]:
    """
    Generate cover text that embeds ``secret`` using token-ID parity.

    If ``encryption_key`` is provided, the secret is first encrypted with
    AES-256-GCM. The resulting bytes are then converted to a bitstring for
    embedding. When decoding, the ciphertext is decrypted using the same key.

    ``temperature`` and ``top_k`` control probabilistic sampling for the next
    token so the generated text looks more natural. ``temperature`` is applied
    to the logits before sampling and ``top_k`` restricts the candidate tokens
    to the ``k`` most likely choices within the desired parity bucket.

    Returns a tuple ``(cover_text, recovered_secret)``.
    """
    # 1) Turn secret into a bit-string
    if encryption_key is not None:
        encrypted = encrypt_message(secret, encryption_key)
        secret_bits = bytes_to_bits(encrypted)
    else:
        secret_bits = encode_secret_message(secret)
    n_bits = len(secret_bits)
    if max_tokens is None:
        max_tokens = n_bits  # one token per bit

    # 2) Tokenize the prompt and prepare generation loop
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(model.device)
    generated_ids = []
    vocab_size = model.config.vocab_size
    parity_mask = torch.arange(vocab_size, device=model.device) % 2

    # 3) For each secret bit, force next token’s parity = that bit
    for i in tqdm(range(min(n_bits, max_tokens)), desc="Embedding bits"):
        bit_val = int(secret_bits[i])  # 0 or 1
        with torch.no_grad():
            logits = model(input_ids=input_ids).logits[0, -1]
        # mask out all tokens whose parity ≠ needed bit
        mask = (parity_mask == bit_val)
        masked_logits = logits.masked_fill(~mask, -float("Inf"))

        if top_k is not None and top_k > 0:
            top_vals, top_idx = torch.topk(masked_logits, top_k)
            probs = torch.nn.functional.softmax(top_vals / temperature, dim=-1)
            sample = torch.multinomial(probs, num_samples=1)
            next_id = top_idx[sample]
        else:
            probs = torch.nn.functional.softmax(masked_logits / temperature, dim=-1)
            next_id = torch.multinomial(probs, num_samples=1)

        # append and continue
        input_ids = torch.cat([input_ids, next_id.unsqueeze(0)], dim=1)
        generated_ids.append(int(next_id))

    # 4) Decode the cover text and recover the secret
    cover_text = tokenizer.decode(
        torch.tensor(generated_ids, device=model.device),
        skip_special_tokens=True
    )
    recovered_bits = "".join(str(tok_id % 2) for tok_id in generated_ids)
    if encryption_key is not None:
        recovered_bytes = bits_to_bytes(recovered_bits)
        recovered_secret = decrypt_message(recovered_bytes, encryption_key)
    else:
        recovered_secret = decode_secret_message(recovered_bits)

    return cover_text, recovered_secret
