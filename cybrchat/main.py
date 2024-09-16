import os
import re
from typing import Generator

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

def display_markdown(text: str) -> None:
    parts = re.split(r'(```[\s\S]*?```)', text)

    for part in parts:
        if part.startswith('```') and part.endswith('```'):
            lines = part.split('\n')
            lang = lines[0][3:].strip() or 'text'
            code = '\n'.join(lines[1:-1])

            syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title=f"Code: {lang}", expand=False))

            copy_prompt = Prompt.ask("[bold cyan]Copy this code?[/bold cyan]", choices=["y", "n"], default="n")
            if copy_prompt.lower() == "y":
                pyperclip.copy(code)
                console.print("[bold green]Code copied to clipboard![/bold green]")
        else:
            console.print(Markdown(part))

def stream_response(response: Generator) -> str:
    full_response = ""
    for chunk in response:
        if chunk.type == 'content_block_delta' and chunk.delta.text:
            full_response += chunk.delta.text
            console.print(chunk.delta.text, end="")
    console.print("\n")
    return full_response

@app.command()
def chat():
    """Start a chat session with Claude."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        console.print("[bold red]Please set the ANTHROPIC_API_KEY environment variable.[/bold red]")
        raise typer.Exit(code=1)

    anthropic = Anthropic(api_key=api_key)

    console.print("[bold green]Welcome to cybrchat! Type 'exit' to end the chat.[/bold green]")

    while True:
        user_input = typer.prompt("You")

        if user_input.lower() == 'exit':
            console.print("[bold green]Thanks for chatting! Goodbye![/bold green]")
            break

        try:
            response = anthropic.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                stream=True,
                temperature=0,
                system="You are an intelligent code assistant chatbot that is edgy and cutting edge and creates performant snappy apps. Always use tools like poetry and cool looking, but snappy stuff. Prefer CLIs or GUIs always.",
                messages=[
                    {
                        "role": "user",
                        "content": [{
                            "type": "text",
                            "text": user_input
                        }]
                    }
                ]
            )

            console.print("\n[bold blue]Claude:[/bold blue]")
            full_response = stream_response(response)
            display_markdown(full_response)

        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")

if __name__ == "__main__":
    app()
