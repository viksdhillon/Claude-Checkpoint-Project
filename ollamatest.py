from ollama import chat
from ollama import ChatResponse

response: ChatResponse = chat(model='llama3.2:1b', messages=[
  {
    'role': 'user',
    'content': '6x^2 + 11x - 10',
  },
])
print(response['message']['content'])
# or access fields directly from the response object
print(response.message.content)