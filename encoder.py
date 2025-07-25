# encoder.py

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Character set for 5-bit encoding
char_set = " abcdefghijklmnopqrstuvwxyz.,!?"
# Build mappings for 5-bit codes
char_to_bin = {}
bin_to_char = {}
for idx, ch in enumerate(char_set):
    code = format(idx, '05b')
    char_to_bin[ch] = code
    bin_to_char[code] = ch

# Reserve '11111' as the uppercase marker
upper_marker = "11111"


def encode_secret_message(text: str) -> str:
    """
    Encode plaintext into a binary string using 5-bit codes.
    Uppercase letters are prefixed by the '11111' marker.
    Characters not in char_set are ignored.
    """
    bits = []
    for ch in text:
        lower = ch.lower()
        if lower in char_to_bin:
            if ch.isupper():
                bits.append(upper_marker)
            bits.append(char_to_bin[lower])
    return "".join(bits)


def decode_secret_message(bit_str: str) -> str:
    """
    Decode a binary string (5-bit codes) back to plaintext.
    Handles '11111' as the uppercase marker for the next character.
    """
    chars = []
    i = 0
    uppercase_next = False
    while i + 5 <= len(bit_str):
        chunk = bit_str[i : i + 5]
        i += 5
        if chunk == upper_marker:
            uppercase_next = True
            continue
        ch = bin_to_char.get(chunk, "")
        if not ch:
            continue
        if uppercase_next:
            ch = ch.upper()
            uppercase_next = False
        chars.append(ch)
    return "".join(chars)



def encrypt_message(secret: str, key: bytes) -> bytes:
    """Encrypt a message using AES-256-GCM and return nonce+ciphertext."""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, secret.encode(), None)


def decrypt_message(data: bytes, key: bytes) -> str:
    """Decrypt data produced by :func:`encrypt_message`."""
    aesgcm = AESGCM(key)
    nonce, ct = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ct, None).decode()


def bytes_to_bits(data: bytes) -> str:
    """Convert bytes to a bit string."""
    return "".join(format(b, "08b") for b in data)


def bits_to_bytes(bits: str) -> bytes:
    """Convert a bit string back to bytes."""
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

