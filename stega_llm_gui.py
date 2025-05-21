# stega_llm_gui.py
# A Tkinter GUI for LLM Steganography (encode & decode)

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from transformers import AutoTokenizer, AutoModelForCausalLM
from stego_generator import generate_stego_text
from stego_decoder import decode_stego_text

class StegaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LLM Steganography GUI")
        self.geometry("900x700")

        # Model selection
        ttk.Label(self, text="Model Name:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.model_var = tk.StringVar(value="gpt2")
        ttk.Entry(self, textvariable=self.model_var, width=30).grid(row=0, column=1, padx=5)
        self.load_btn = ttk.Button(self, text="Load Model", command=self.load_model)
        self.load_btn.grid(row=0, column=2, padx=5)
        self.status = ttk.Label(self, text="Model not loaded", foreground="red")
        self.status.grid(row=0, column=3, padx=5)

        # Encode section
        ttk.Label(self, text="--- Encode Secret to Cover Text ---").grid(row=1, column=0, columnspan=4, pady=(10,0))
        ttk.Label(self, text="Cover Prompt:").grid(row=2, column=0, sticky="nw", padx=5, pady=5)
        self.prompt_text = scrolledtext.ScrolledText(self, width=80, height=4)
        self.prompt_text.grid(row=2, column=1, columnspan=3, padx=5, pady=5)
        self.prompt_text.insert(tk.END, "You are interviewing a security researcher about advanced steganography techniques.")

        ttk.Label(self, text="Secret Message:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.secret_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.secret_var, width=60).grid(row=3, column=1, columnspan=2, padx=5, pady=5)
        self.encode_btn = ttk.Button(self, text="Generate Stego Text", command=self.on_generate)
        self.encode_btn.grid(row=3, column=3, padx=5)

        ttk.Label(self, text="Cover Text:").grid(row=4, column=0, sticky="nw", padx=5, pady=5)
        self.cover_text = scrolledtext.ScrolledText(self, width=80, height=8)
        self.cover_text.grid(row=4, column=1, columnspan=3, padx=5, pady=5)

        # Decode section
        ttk.Label(self, text="--- Decode Secret from Cover Text ---").grid(row=5, column=0, columnspan=4, pady=(20,0))
        ttk.Label(self, text="Cover Text to Decode:").grid(row=6, column=0, sticky="nw", padx=5, pady=5)
        self.decode_input = scrolledtext.ScrolledText(self, width=80, height=8)
        self.decode_input.grid(row=6, column=1, columnspan=3, padx=5, pady=5)
        self.decode_btn = ttk.Button(self, text="Decode Secret", command=self.on_decode)
        self.decode_btn.grid(row=7, column=3, pady=5)
        ttk.Label(self, text="Decoded Secret:").grid(row=8, column=0, sticky="nw", padx=5, pady=5)
        self.decoded_text = scrolledtext.ScrolledText(self, width=80, height=2)
        self.decoded_text.grid(row=8, column=1, columnspan=3, padx=5, pady=5)

        # Disable actions until model loaded
        self.model = None
        self.tokenizer = None
        self.encode_btn.config(state=tk.DISABLED)
        self.decode_btn.config(state=tk.DISABLED)

    def load_model(self):
        model_name = self.model_var.get().strip()
        if not model_name:
            messagebox.showerror("Error", "Please enter a model name.")
            return
        self.status.config(text="Loading...", foreground="orange")
        self.load_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._load_model_thread, args=(model_name,), daemon=True).start()

    def _load_model_thread(self, model_name):
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            model.eval()
            self.tokenizer = tokenizer
            self.model = model
            self.status.config(text="Model loaded", foreground="green")
            self.encode_btn.config(state=tk.NORMAL)
            self.decode_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Load Error", str(e))
            self.status.config(text="Load failed", foreground="red")
        finally:
            self.load_btn.config(state=tk.NORMAL)

    def on_generate(self):
        if not self.model:
            return
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        secret = self.secret_var.get().strip()
        if not secret:
            messagebox.showerror("Error", "Secret message cannot be empty.")
            return
        self.encode_btn.config(state=tk.DISABLED)
        self.cover_text.delete("1.0", tk.END)
        threading.Thread(target=self._generate_thread, args=(prompt, secret), daemon=True).start()

    def _generate_thread(self, prompt, secret):
        try:
            cover, _ = generate_stego_text(self.model, self.tokenizer, prompt, secret)
            self.cover_text.insert(tk.END, cover)
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))
        finally:
            self.encode_btn.config(state=tk.NORMAL)

    def on_decode(self):
        if not self.model:
            return
        cover = self.decode_input.get("1.0", tk.END).strip()
        if not cover:
            messagebox.showerror("Error", "Cover text cannot be empty.")
            return
        self.decode_btn.config(state=tk.DISABLED)
        self.decoded_text.delete("1.0", tk.END)
        threading.Thread(target=self._decode_thread, args=(cover,), daemon=True).start()

    def _decode_thread(self, cover):
        try:
            secret = decode_stego_text(self.model, self.tokenizer, cover)
            self.decoded_text.insert(tk.END, secret)
        except Exception as e:
            messagebox.showerror("Decoding Error", str(e))
        finally:
            self.decode_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = StegaApp()
    app.mainloop()
