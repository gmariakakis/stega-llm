# stega_llm_gui.py
# Modern Tkinter GUI for steganography with LLMs

import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from transformers import AutoModelForCausalLM, AutoTokenizer

from stego_generator import generate_stego_text
from stego_decoder import decode_stego_text


class StegaApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("LLM Steganography")
        self.geometry("960x740")
        style = ttk.Style(self)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure("TLabel", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))

        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        # Model loading controls
        top = ttk.Frame(main)
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Model name:").grid(row=0, column=0, sticky="w")
        self.model_var = tk.StringVar(value="gpt2")
        ttk.Entry(top, textvariable=self.model_var, width=30).grid(row=0, column=1, padx=5)
        self.load_btn = ttk.Button(top, text="Load", command=self.load_model)
        self.load_btn.grid(row=0, column=2, padx=5)
        self.status = ttk.Label(top, text="Model not loaded", foreground="red")
        self.status.grid(row=0, column=3, padx=5)

        notebook = ttk.Notebook(main)
        notebook.pack(fill="both", expand=True)

        self.encode_tab = ttk.Frame(notebook)
        self.decode_tab = ttk.Frame(notebook)
        notebook.add(self.encode_tab, text="Encode")
        notebook.add(self.decode_tab, text="Decode")

        self._build_encode_tab()
        self._build_decode_tab()

        # model objects
        self.model = None
        self.tokenizer = None
        self.encode_btn.config(state=tk.DISABLED)
        self.decode_btn.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    def _build_encode_tab(self) -> None:
        f = self.encode_tab
        ttk.Label(f, text="Cover prompt:").grid(row=0, column=0, sticky="nw", pady=2)
        self.prompt_text = scrolledtext.ScrolledText(f, width=80, height=5)
        self.prompt_text.grid(row=0, column=1, padx=5, pady=2)
        self.prompt_text.insert(
            tk.END,
            "You are interviewing a security researcher about advanced steganography techniques.",
        )

        ttk.Label(f, text="Secret message:").grid(row=1, column=0, sticky="w", pady=2)
        self.secret_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.secret_var, width=60).grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(f, text="AES key (hex, optional):").grid(row=2, column=0, sticky="w", pady=2)
        self.key_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.key_var, width=70).grid(row=2, column=1, sticky="w", padx=5)

        self.encode_btn = ttk.Button(f, text="Generate", command=self.on_generate)
        self.encode_btn.grid(row=3, column=1, sticky="e", pady=5)

        ttk.Label(f, text="Cover text:").grid(row=4, column=0, sticky="nw", pady=2)
        self.cover_text = scrolledtext.ScrolledText(f, width=80, height=10)
        self.cover_text.grid(row=4, column=1, padx=5, pady=2)

    # ------------------------------------------------------------------
    def _build_decode_tab(self) -> None:
        f = self.decode_tab
        ttk.Label(f, text="Cover text to decode:").grid(row=0, column=0, sticky="nw", pady=2)
        self.decode_input = scrolledtext.ScrolledText(f, width=80, height=10)
        self.decode_input.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(f, text="AES key (hex, optional):").grid(row=1, column=0, sticky="w", pady=2)
        self.decode_key_var = tk.StringVar()
        ttk.Entry(f, textvariable=self.decode_key_var, width=70).grid(row=1, column=1, sticky="w", padx=5)

        self.decode_btn = ttk.Button(f, text="Decode", command=self.on_decode)
        self.decode_btn.grid(row=2, column=1, sticky="e", pady=5)

        ttk.Label(f, text="Decoded secret:").grid(row=3, column=0, sticky="nw", pady=2)
        self.decoded_text = scrolledtext.ScrolledText(f, width=80, height=3)
        self.decoded_text.grid(row=3, column=1, padx=5, pady=2)

    # ------------------------------------------------------------------
    def load_model(self) -> None:
        name = self.model_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Please enter a model name.")
            return
        self.status.config(text="Loading...", foreground="orange")
        self.load_btn.config(state=tk.DISABLED)
        threading.Thread(target=self._load_model_thread, args=(name,), daemon=True).start()

    def _load_model_thread(self, name: str) -> None:
        try:
            tokenizer = AutoTokenizer.from_pretrained(name)
            model = AutoModelForCausalLM.from_pretrained(name)
            model.eval()
            self.tokenizer = tokenizer
            self.model = model
            self.status.config(text="Model loaded", foreground="green")
            self.encode_btn.config(state=tk.NORMAL)
            self.decode_btn.config(state=tk.NORMAL)
        except Exception as exc:
            messagebox.showerror("Load Error", str(exc))
            self.status.config(text="Load failed", foreground="red")
        finally:
            self.load_btn.config(state=tk.NORMAL)

    # ------------------------------------------------------------------
    def parse_key(self, value: str):
        value = value.strip()
        if not value:
            return None
        try:
            key = bytes.fromhex(value)
        except ValueError:
            messagebox.showerror("Key Error", "Key must be hex encoded")
            return None
        if len(key) != 32:
            messagebox.showerror("Key Error", "Key must be 32 bytes (64 hex chars)")
            return None
        return key

    def on_generate(self) -> None:
        if not self.model:
            return
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        secret = self.secret_var.get().strip()
        if not secret:
            messagebox.showerror("Error", "Secret message cannot be empty.")
            return
        key = self.parse_key(self.key_var.get())
        if self.key_var.get().strip() and key is None:
            return
        self.encode_btn.config(state=tk.DISABLED)
        self.cover_text.delete("1.0", tk.END)
        threading.Thread(target=self._generate_thread, args=(prompt, secret, key), daemon=True).start()

    def _generate_thread(self, prompt: str, secret: str, key) -> None:
        try:
            cover, _ = generate_stego_text(
                self.model,
                self.tokenizer,
                prompt,
                secret,
                encryption_key=key,
            )
            self.cover_text.insert(tk.END, cover)
        except Exception as exc:
            messagebox.showerror("Generation Error", str(exc))
        finally:
            self.encode_btn.config(state=tk.NORMAL)

    def on_decode(self) -> None:
        if not self.model:
            return
        cover = self.decode_input.get("1.0", tk.END).strip()
        if not cover:
            messagebox.showerror("Error", "Cover text cannot be empty.")
            return
        key = self.parse_key(self.decode_key_var.get())
        if self.decode_key_var.get().strip() and key is None:
            return
        self.decode_btn.config(state=tk.DISABLED)
        self.decoded_text.delete("1.0", tk.END)
        threading.Thread(target=self._decode_thread, args=(cover, key), daemon=True).start()

    def _decode_thread(self, cover: str, key) -> None:
        try:
            secret = decode_stego_text(
                self.model, self.tokenizer, cover, encryption_key=key
            )
            self.decoded_text.insert(tk.END, secret)
        except Exception as exc:
            messagebox.showerror("Decoding Error", str(exc))
        finally:
            self.decode_btn.config(state=tk.NORMAL)


if __name__ == "__main__":
    app = StegaApp()
    app.mainloop()
