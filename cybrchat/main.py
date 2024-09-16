import os
import requests
import json
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import TerminalFormatter
import re
from anthropic import Anthropic

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
    anthropic = Anthropic(api_key=api_key)
    user_input = input("You: ")
    try:
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            stream=True,
            temperature=0,
            system="You are an intelligent code assistant chatbot that is edgy and cutting edge and creates performant snappy apps. always use tools like poetry and cool looking, but snappy stuff. i prefer CLIs or GUIs always",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": user_input
                        }
                    ]
                }
            ]
        )

        full_response = ""
        for chunk in response:
            if hasattr(chunk, 'type') and chunk.type == 'content_block_delta':
                if hasattr(chunk.delta, 'text'):
                    full_response += chunk.delta.text
    except Exception as e:
        print(e)
        return

if __name__ == "__main__":
    chat_with_claude()
