# stega-llm
# Instructions 
1) git clone https://github.com/gmariakakis/stega-llm.git
2) cd stega-llm
 #Requires-Python >=3.9,<3.12 
3) python -m venv stegenv && source stegenv/Scripts/activate   # Windows: stegenv\Scripts\activate
# Install dependencies and launch the GUI
4) pip install -r requirements.txt  # adjust if you need CUDA
5) python stega_llm_gui.py
6) Use any Hugging Face model, just copy & paste the name. Recommended Light: openai-community/gpt2
                                                                       Medium:  mistralai/Mistral-7B-Instruct-v0.1 or ousResearch/Llama-2-7b-hf

The revamped GUI allows you to optionally specify a 32-byte AES key when encoding
or decoding a message. Leave the key fields empty to disable encryption.

#The heavier the model the better the cover text will be .

## Probabilistic encoding

The ``generate_stego_text`` function now supports probabilistic sampling.
You can pass ``temperature`` and ``top_k`` parameters to control how tokens
are sampled when embedding a secret. Lower temperatures make the output more
deterministic, while ``top_k`` restricts sampling to the ``k`` most likely
candidates of the desired parity.

## AES-256 encryption

Secrets are now encrypted with AES-256-GCM before being embedded. Pass an
``encryption_key`` (32 bytes) to ``generate_stego_text`` and
``decode_stego_text`` to secure the message. The key must be kept secret and
shared with the recipient for decryption.

