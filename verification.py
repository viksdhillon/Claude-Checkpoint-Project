from ollama import chat
from ollama import ChatResponse
from checkpoint_structure import CheckpointADT

class VerificationSystem():
    def __init__(self, checkpointSystem):
        self.checkpointSystem = checkpointSystem
    
    def generate_verification(query, response):
        response: ChatResponse = chat(model='llama3.2:1b', messages=[
            {
                'role': 'user',
                'content': f'Given the following query: {query} | and the following response {response} | please create a verification question ',
            },
        ])
        