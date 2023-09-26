import sys

import torch
from llama_index import PromptHelper
from peft.peft_model import PeftModel
from transformers import GenerationConfig, LlamaForCausalLM, LlamaTokenizer, BatchEncoding
from utils.prompter import Prompter

sys.path.append('./alpaca-lora')

# define prompt helper
# set maximum input size
max_input_size = 2048
# set number of output tokens
num_output = 256
# set maximum chunk overlap
max_chunk_overlap = 20
prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)


class AlpacaLora:
    def __init__(self):
        self.lora_weights = 'chansung/gpt4-alpaca-lora-13b'
        # self.lora_weights = 'tloen/alpaca-lora-7b'
        # self.lora_weights = '../alpaca-lora/lora-alpaca-yan'
        # self.base_model = 'decapoda-research/llama-7b-hf'
        self.base_model = 'decapoda-research/llama-13b-hf'
        self.model_name = f'{self.base_model} + {self.lora_weights}'
        print(f'Loading model {self.model_name}...')

        self.prompter = Prompter('alpaca')
        self.tokenizer = LlamaTokenizer.from_pretrained(self.base_model)
        self.model = LlamaForCausalLM.from_pretrained(self.base_model, load_in_8bit=True,
            torch_dtype=torch.bfloat16, device_map="auto", )
        self.model = PeftModel.from_pretrained(self.model, self.lora_weights, torch_dtype=torch.bfloat16)

        # unwind broken decapoda-research config
        self.model.config.pad_token_id = self.tokenizer.pad_token_id = 0  # unk
        self.model.config.bos_token_id = 1
        self.model.config.eos_token_id = 2

        self.model.eval()
        if torch.__version__ >= "2" and sys.platform != "win32":
            self.model = torch.compile(self.model)
        print('Model loaded.')

        self.temperature = 0
        self.top_p = 0.75
        self.top_k = 40
        self.num_beams = 1
        self.max_new_tokens = 512
        self.generation_config = GenerationConfig(temperature=self.temperature, top_p=self.top_p,
            top_k=self.top_k, num_beams=self.num_beams, )

        self.device = 'cuda'

    def generate(self, system_prompt: str, input_prompt: str = '') -> str:
        inputs: BatchEncoding = self.tokenizer(input_prompt, return_tensors="pt")
        input_ids = inputs["input_ids"]
        if input_ids.shape[1] > 1800:
            input_prompt = self.tokenizer.decode(input_ids[0, :1800])

        prompt = self.prompter.generate_prompt(system_prompt, input_prompt)
        inputs = self.tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.device)
        if input_ids.shape[1] > 2000:
            input_ids = input_ids[:, :2000]
        print(input_ids.shape)
        with torch.no_grad():
            generation_output = self.model.generate(input_ids=input_ids,
                generation_config=self.generation_config, return_dict_in_generate=True, output_scores=True,
                max_new_tokens=self.max_new_tokens, )
        s = generation_output.sequences[0]
        print(s.shape)
        output = self.tokenizer.decode(s)
        return self.prompter.get_response(output)
