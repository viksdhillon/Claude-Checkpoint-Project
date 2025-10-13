from checkpoint_structure import CheckpointADT
from ollama import chat
from ollama import ChatResponse
import json

class SaveQuery(CheckpointADT):
    def __init__(self):
        super().__init__()
    
    #Factor the polynomial 6x^2 + 11x - 10. Give me the answer like for example (3x + 5)(6x + 2). Please write each step out distinctively. The first step should be "STEP 1: ..., second step "STEP 2: ... YOU SHOULD NOT HAVE MORE THAN 5 STEPS
    
