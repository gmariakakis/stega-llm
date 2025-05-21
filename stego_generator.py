# stego_generator.py

import torch
from tqdm.auto import tqdm
from encoder import encode_secret_message, decode_secret_message
from typing import Tuple

def generate_stego_text(
    model,
    tokenizer,
    prompt: str,
    secret: str,
    max_tokens: int = None
) -> Tuple[str, str]:
    """
    Generate cover text that embeds `secret` (via one bit per token, using token-ID parity).
    Returns a tuple: (cover_text, recovered_secret).
    """
    # 1) Turn secret into a bit‐string
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
        next_id = torch.argmax(masked_logits).unsqueeze(0)
        # append and continue
        input_ids = torch.cat([input_ids, next_id.unsqueeze(0)], dim=1)
        generated_ids.append(int(next_id))

    # 4) Decode the cover text and recover the secret
    cover_text = tokenizer.decode(
        torch.tensor(generated_ids, device=model.device),
        skip_special_tokens=True
    )
    recovered_bits = "".join(str(tok_id % 2) for tok_id in generated_ids)
    recovered_secret = decode_secret_message(recovered_bits)

    return cover_text, recovered_secret
