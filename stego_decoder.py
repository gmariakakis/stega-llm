# stego_decoder.py
# Backend for decoding a hidden secret from cover text

import torch
from encoder import decode_secret_message


def decode_stego_text(model, tokenizer, cover_text: str) -> str:
    """
    Decode the hidden secret from `cover_text` by tokenizing via the given tokenizer,
    mapping each token ID's parity to a bit (even=0, odd=1), then translating the
    bitstring back to plaintext using the shared 5-bit alphabet.

    Returns the recovered secret string.
    """
    # Tokenize the cover text (skip special tokens)
    inputs = tokenizer(cover_text, return_tensors="pt")
    input_ids = inputs.input_ids.to(model.device)

    # Flatten to 1D and convert token IDs to bits (parity)
    token_ids = input_ids[0]
    bits = "".join(str(int(tok_id % 2)) for tok_id in token_ids)

    # Decode bits to plaintext
    secret = decode_secret_message(bits)
    return secret
