# cybrchat

This project implements a chat interface to interact with Claude via the Anthropic API. It displays the output in markdown format with "copy code" buttons for code segments.

## Setup

1. Make sure you have Poetry installed: https://python-poetry.org/docs/#installation

2. Clone the repository:
   ```
   git clone https://github.com/yourusername/cybrchat.git
   cd cybrchat
   ```

3. Install dependencies:
   ```
   poetry install
   ```

4. Set your Anthropic API key as an environment variable:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

## Usage

Run the script:

```
poetry run python cybrchat/main.py
```

Type your messages and press Enter to send them to Claude. Type 'exit' or 'quit' to end the conversation.

## Development

- Run tests: `poetry run pytest`
- Format code: `poetry run black .`
- Sort imports: `poetry run isort .`
- Type checking: `poetry run mypy .`

Enjoy chatting with Claude!
