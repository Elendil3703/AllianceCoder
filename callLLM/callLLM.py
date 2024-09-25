import torch
from colorama import Fore, Style
from transformers import AutoTokenizer, AutoModelForCausalLM
from callLLM.sampling.autoregressive_sampling import autoregressive_sampling
from callLLM.sampling.globals import Decoder
def color_print(text):
    print(Fore.RED + text + Style.RESET_ALL)

def generate(input_text,model_name, num_tokens,top_k,top_p,confidence_threshold):
    torch_device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    Decoder().set_tokenizer(tokenizer)
    
    print(f"begin loading models:  \n {model_name}")
    
    model = AutoModelForCausalLM.from_pretrained(model_name, 
                                                       torch_dtype=torch.float16,
                                                       device_map="auto",
                                                       trust_remote_code=True)
    print("finish loading models")
    
    input_ids = tokenizer.encode(input_text, return_tensors='pt').to(torch_device)
    

    # Large model autoregressive sampling and benchmark
    torch.manual_seed(123)
    output = autoregressive_sampling(input_ids, model, num_tokens, top_k=top_k, top_p=top_p, confidence_threshold=confidence_threshold)
    generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
    #output_text = generated_text.replace(input_text, "") #去掉输入的prompt
    #return output_text
    return generated_text
    


