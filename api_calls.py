import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable - NEVER hardcode it!
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

try:
    message = client.messages.create(
        model="claude-sonnet-4-20250514",  # Updated model
        max_tokens=1000,
        messages=[
            {
                "role": "user",
                "content": "What should I search for to find the latest developments in renewable energy?"
            }
        ]
    )
    
    print(message.content)
    
except anthropic.APIError as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")