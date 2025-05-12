from litellm import completion
import os

os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')

response = completion(
    model="gemini/gemini-2.0-flash", 
    messages=[{"role": "user", "content": "こんにちは！"}]
)

print(response['choices'][0]['message']['content'])
