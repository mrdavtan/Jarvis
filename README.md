# Jarvis: AI-Powered Directory Navigation and Interaction

![Jarvis AI Assistant](jarvis_ai_assistant.png)

Jarvis is an AI-powered assistant module for navigation and interaction with your local file system. Inspired by the AI character Jarvis from the Iron Man movie, this module provides a seamless and intuitive way to explore and manipulate files and directories using natural language commands.

## Features

- Voice-controlled directory navigation
- File and directory manipulation (copy, remove, execute)
- Configuration-based directory shortcuts
- Integration with OpenAI's language model for natural language understanding
- Extensible architecture for adding custom commands and functionalities

## Installation

1. Clone the repository and go to the project root:


```bash

git clone https://github.com/yourusername/Jarvis.git

cd Jarvis

```

2. Creating a virtual env is optional:
```bash

python -m venv .venv

source .venv/bin/activate


```



3. Install the required dependencies:

```bash

pip install -r requirements.txt


```

4. Set up your OpenAI API key:
- Create a `.env` file in the project root directory.
- Add your OpenAI API key to the file: `OPENAI_API_KEY=your_api_key_here`

5. Configure directory shortcuts (optional):
- Open the `config.json` file.
- Add your desired directory shortcuts in the following format:
  ```json
  {
    "directories": {
      "shortcut_name": "/path/to/directory"
    }
  }
  ```

## Usage

1. Run the Jarvis assistant:

```bash

python main_agent.py

```

2. Interact with Jarvis using voice commands or text input. Some example commands:
- "Go to the 'documents' directory"
- "List the contents of the current directory"
- "Execute the 'script.sh' file"
- "Copy 'file.txt' to the 'backup' directory"
- "Remove the 'temp' directory"

3. To exit the assistant, simply say or type "exit".

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request. Make sure to follow the existing code style and include appropriate tests.

## License

This project is licensed under the [MIT License](LICENSE).


