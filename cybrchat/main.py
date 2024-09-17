import os
import re
from typing import Generator, List, Dict

import typer
import pyperclip
from anthropic import Anthropic
from rich import print
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt

app = typer.Typer()
console = Console()

def escape_markup(text: str) -> str:
    """Escape Rich markup characters in a string."""
    return re.sub(r"(\[|\])", r"\\\1", text)

def display_markdown(text: str, is_incomplete: bool) -> None:
    parts = re.split(r'(```[\s\S]*?```)', text)

    for part in parts:
        if part.startswith('```'):
            lines = part.split('\n')
            lang = lines[0][3:].strip() or 'bash'
            code = '\n'.join(lines[1:-1])

            syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Code: {lang}" + (" (Partial)" if is_incomplete else ""), expand=False))
        else:
            console.print(Markdown(escape_markup(part)))

    if is_incomplete:
        console.print("[yellow]Note: The response was truncated due to length limitations.[/yellow]")

def stream_response(response: Generator) -> tuple[str, bool]:
    full_response = ""
    for chunk in response:
        if chunk.type == 'content_block_delta' and chunk.delta.text:
            full_response += chunk.delta.text
            print(escape_markup(chunk.delta.text), end="", flush=True)  # Print each chunk as it arrives

    print("\n")  # Add a newline after the response
    return full_response

def get_complete_response(anthropic: Anthropic, conversation_history: List[Dict[str, List[Dict[str, str]]]]) -> str:
    full_response = ""
    complete_script = ""
    is_incomplete = True
    MAX_ITERATIONS = 5  # Limit the number of continuations to prevent infinite loops

    for _ in range(MAX_ITERATIONS):
        response = anthropic.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            stream=True,
            temperature=0,
            system="You are an intelligent code assistant chatbot that is edgy and cutting edge and creates performant snappy apps. Always use tools like poetry and cool looking, but snappy stuff. Prefer CLIs or GUIs always. When prompted to build a project or something similar, you should provide a comprehensive, snappy, error-free bash script to setup the entire project from start to finish without any hiccups. Every project should have everything-included at an industry standard or better. if using python (not necessary), use poetry over pip. make sure your code has no placeholder comments. ONLY PRESENT THE FINAL BASH SCRIPT AND NOTHING ELSE. THIS IS THE MOST IMPORTANT PART do not include too much stuff. be space efficient. AND IT SHOULD BE THE ONLY THING IN YOUR OUTPUT. Keep your response concise and to the point.MAKE SURE THERE ARE NO ERRORS WHEN IT IS RAN. RETHINK YOUR WORK BEFORE YOU TYPE. ALWAYS MAKE EVERYTHING HAVE A UNIQUE MODERN CLEAN SLEEK CYBERPUNK LOOK. ",
            messages=conversation_history
        )

        part_response = stream_response(response)
        full_response += part_response
        complete_script += part_response

        # Check if the response is complete (ends with a closing code block)
        if complete_script.strip().endswith("```"):
            is_incomplete = False
            break

        if is_incomplete:
            conversation_history.append({"role": "assistant", "content": [{"type": "text", "text": part_response}]})
            conversation_history.append({"role": "user", "content": [{"type": "text", "text": "Please continue the script from where you left off, without repeating anything or starting a new code block. Keep it brief."}]})

    # Remove any leading/trailing backticks and language specifiers
    complete_script = re.sub(r'^```\w*\n', '', complete_script.strip())
    complete_script = re.sub(r'\n```$', '', complete_script)

    return complete_script

@app.command()
def chat():
    """Start a chat session with Claude."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        console.print("Please set the ANTHROPIC_API_KEY environment variable.", style="bold red")
        raise typer.Exit(code=1)

    anthropic = Anthropic(api_key=api_key)

    console.print("Welcome to cybrchat! Type 'exit' to end the chat.", style="bold green")

    while True:
        user_input = typer.prompt("You")

        if user_input.lower() == 'exit':
            console.print("Thanks for chatting! Goodbye!", style="bold green")
            break

        try:
            conversation_history = [
                {
                    "role": "user",
                    "content": [{
                        "type": "text",
                        "text": user_input
                    }]
                }
            ]

            console.print("\nClaude:", style="bold blue")
            complete_script = get_complete_response(anthropic, conversation_history)
            display_markdown(complete_script, False)

            # Offer to copy the complete script
            copy_prompt = Prompt.ask("[bold cyan]Copy the complete script?[/bold cyan]", choices=["y", "n"], default="n")
            if copy_prompt.lower() == "y":
                pyperclip.copy(complete_script)
                console.print("[bold green]Complete script copied to clipboard![/bold green]")
                # Debug output
                console.print("[dim]Debug: First 100 characters of copied script:[/dim]")
                console.print(f"[dim]{complete_script[:100]}...[/dim]")

        except Exception as e:
            error_type = escape_markup(type(e).__name__)
            error_details = escape_markup(str(e))
            console.print(f"An error occurred: {error_type}", style="bold red")
            if error_details:
                console.print(f"Error details: {error_details}", style="red")
            console.print("If this error persists, please check your API key and network connection.", style="yellow")

if __name__ == "__main__":
    app()
