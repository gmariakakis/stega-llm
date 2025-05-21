# main.py

from transformers import AutoTokenizer, AutoModelForCausalLM
from stego_generator import generate_stego_text

if __name__ == "__main__":
    # 1) Choose your model (any causal LM from HuggingFace)
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    model.eval()

    # 2) Define a cover prompt and your secret
    prompt = "You are interviewing a security researcher about advanced steganography techniques."
    secret_message = "Hello World"

    print(f"Secret to hide: {secret_message}\n")

    # 3) Embed & then immediately recover for verification
    cover, recovered = generate_stego_text(model, tokenizer, prompt, secret_message)

    print("--- Generated Cover Text ---")
    print(cover)
    print("\n--- Recovered Secret ---")
    print(recovered)
