import os
from ollama import chat
from ollama import ChatResponse
from checkpoint_structure import CheckpointADT

# Uses default path from CheckpointADT (automatically points to project directory)
checkpoint = CheckpointADT()
checkpoint.prompt_and_save('Factor the polynomial 6x^2 + 11x - 10. Give me the answer like for example (3x + 5)(6x + 2). Please write each step out distinctively as STEP 1: ..., STEP 2: ..., etc. YOU *MUST* write it out in steps.',"STEP")
#print(checkpoint.get(1))
print(checkpoint.toString())
checkpoint.rollback_to(2)
print(checkpoint.toString())
checkpoint.append("hi", "This is not the right answer")
print(checkpoint.toString())
checkpoint.delete_node_by_id(1)
print(checkpoint.toString())
