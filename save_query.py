from checkpoint_structure import CheckpointADT
from ollama import chat
from ollama import ChatResponse
import json

class SaveQuery(CheckpointADT):
    def __init__(self, log="checkpoint_save.json"):
        super().__init__()
        self.log = log
    
    def prompt_and_save(self, query, checkpoint):
        response: ChatResponse = chat(model='llama3.2:1b', messages=[
            {
                'role': 'user',
                'content': query,
            },
        ])
        steps = self.scrape_data("STEP", response.message.content)
        for i in steps:
            checkpoint.append(query, i)
    
        

    def scrape_data(self, delim, message):
        steps = message.split(delim)
        return steps

    #Factor the polynomial 6x^2 + 11x - 10. Give me the answer like for example (3x + 5)(6x + 2). Please write each step out distinctively. The first step should be "STEP 1: ..., second step "STEP 2: ... YOU SHOULD NOT HAVE MORE THAN 5 STEPS
    
