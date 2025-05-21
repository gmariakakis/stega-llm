# stega-llm
# bash commands
1) git clone https://github.com/gmariakakis/stega-llm.git
2) cd stega-llm
 #Requires-Python >=3.9,<3.12 
3) python -m venv stegenv && source stegenv/Scripts/activate   # Windows: stegenv\Scripts\activate
4) pip install -r requirements.txt  #adjust if you need CUDA 
5) python stega_llm_gui.py
6) use any of huggingface model .Recommended Light : openai-community/gpt2
                                           Medium  : mistralai/Mistral-7B-Instruct-v0.1  or ousResearch/Llama-2-7b-hf
#The heavier the model the better the cover text will be .                 

