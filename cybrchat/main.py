import os
import requests
import json
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import re

def display_markdown(text):
    parts = re.split(r'()', text)
    
    for part in parts:
        if part.startswith(''):
            lines = part.split('\n')
            lang = lines[0][3:].strip() or 'text'
            code = '\n'.join(lines[1:-1])
            
            lexer = get_lexer_by_name(lang, stripall=True)
            formatter = TerminalFormatter()
            highlighted_code = highlight(code, lexer, formatter)
            
            print("\n" + "=" * 40)
            print(f"Copy code (language: {lang}):")
            print("=" * 40)
            print(highlighted_code)
            print("=" * 40 + "\n")
        else:
            print(part)

def chat_with_claude():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("Please set the ANTHROPIC_API_KEY environment variable.")
        return

    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key,
    }

    conversation = []

    while True:
        user_input = input("You: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        conversation.append({"role": "human", "content": user_input})

        data = {
            'model': 'claude-3-sonnet-20240229',
            'messages': conversation,
            'max_tokens': 1000,
        }

        response = requests.post('https://api.anthropic.com/v1/messages', headers=headers, json=data)

        if response.status_code == 200:
            assistant_reply = response.json()['content'][0]['text']
            conversation.append({"role": "assistant", "content": assistant_reply})
            print("\nClaude:")
            display_markdown(assistant_reply)
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    chat_with_claude()
