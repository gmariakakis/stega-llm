# stego_decoder.py
# Backend for decoding a hidden secret from cover text

from encoder import (
    decode_secret_message,
    decrypt_message,
    bits_to_bytes,
)


def decode_stego_text(model, tokenizer, cover_text: str, *, encryption_key: bytes | None = None) -> str:
    """
    Decode the hidden secret from `cover_text` by tokenizing via the given tokenizer,
    mapping each token ID's parity to a bit (even=0, odd=1), then translating the
    bitstring back to plaintext using the shared 5-bit alphabet. If
    ``encryption_key`` is provided, the recovered bits are decrypted using
    AES-256-GCM before decoding.

    Returns the recovered secret string.
    """
    # Tokenize the cover text (skip special tokens)
    inputs = tokenizer(cover_text, return_tensors="pt")
    input_ids = inputs.input_ids.to(model.device)

    # Flatten to 1D and convert token IDs to bits (parity)
    token_ids = input_ids[0]
    bits = "".join(str(int(tok_id % 2)) for tok_id in token_ids)

    # Decode bits to plaintext
    if encryption_key is not None:
        data = bits_to_bytes(bits)
        secret = decrypt_message(data, encryption_key)
    else:
        secret = decode_secret_message(bits)
    return secret
