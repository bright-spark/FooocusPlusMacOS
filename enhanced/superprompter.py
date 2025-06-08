import os
import random
import torch
from common import ROOT
from common import torch_device
from transformers import T5Tokenizer, T5ForConditionalGeneration
import modules.config as config
import shutil

tokenizer = None
model = None
modelDir = os.path.join(config.paths_llms[0], "superprompt-v1" )


def answer(input_text="", max_new_tokens=256, repetition_penalty=1.2, temperature=0.5, top_p=1, top_k = 1 , seed=-1):
    global tokenizer, model, modelDir

    if 'tokenizer' not in globals() or 'model' not in globals():
        globals()['tokenizer'] = None
        globals()['model'] = None
    if tokenizer is None or model is None:
        if not os.path.exists(os.path.join(modelDir, "model.safetensors")):
            print("[SuperPrompt] Downloading the model files for Superprompter. \n")
            config.downloading_superprompter_model()

        tokenizer = T5Tokenizer.from_pretrained(modelDir)
        model = T5ForConditionalGeneration.from_pretrained(modelDir, torch_dtype=torch.float16).to(torch_device)


    input_ids = tokenizer(input_text, return_tensors="pt").input_ids.to(torch_device)

    outputs = model.generate(input_ids, max_new_tokens=max_new_tokens, repetition_penalty=repetition_penalty,
                            do_sample=True, temperature=temperature, top_p=top_p, top_k=top_k)

    dirty_text = tokenizer.decode(outputs[0])
    text = dirty_text.replace("<pad>", "").replace("</s>", "").strip()
    
    return text

def remove_superprompt():
    global tokenizer, model

    if 'tokenizer' not in globals():
        del tokenizer
    if 'model' not in globals():
        del model
    return

