import os
import json
from openai import OpenAI, AssistantEventHandler
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
import os

client = OpenAI()

assistant = client.beta.assistants.create(
    instructions="You are a directory navigation assistant. Use the provided functions to navigate and list directory contents.",
    model="gpt-4-turbo",
    tools=[
        {
            "type": "function",
            "function": {
                "name": "list_directory_contents",
                "description": "List the contents of the current directory",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "change_directory",
                "description": "Change the current directory",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "The directory to change to (relative or absolute path)"
                        }
                    },
                    "required": ["directory"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_current_directory",
                "description": "Get the current working directory",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }
    ]
)

current_directory = os.getcwd()

class EventHandler(AssistantEventHandler):
    def on_event(self, event):
        global current_directory
        if event.event == 'thread.run.requires_action':
            run_id = event.data.id
            self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
        global current_directory
        tool_outputs = []

        for tool in data.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "list_directory_contents":
                contents = os.listdir(current_directory)
                tool_outputs.append({"tool_call_id": tool.id, "output": ", ".join(contents)})
            elif tool.function.name == "change_directory":
                directory = json.loads(tool.function.arguments)["directory"]
                new_directory = os.path.abspath(os.path.join(current_directory, directory))
                if os.path.exists(new_directory) and os.path.isdir(new_directory):
                    current_directory = new_directory
                    tool_outputs.append({"tool_call_id": tool.id, "output": f"Changed current directory to {current_directory}"})
                else:
                    tool_outputs.append({"tool_call_id": tool.id, "output": "Invalid directory"})
            elif tool.function.name == "get_current_directory":
                tool_outputs.append({"tool_call_id": tool.id, "output": current_directory})

        self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
        with client.beta.threads.runs.submit_tool_outputs_stream(
            thread_id=self.current_run.thread_id,
            run_id=self.current_run.id,
            tool_outputs=tool_outputs,
            event_handler=EventHandler(),
        ) as stream:
            for text in stream.text_deltas:
                print(text, end="", flush=True)
            print()

while True:
    user_input = input("User: ")
    if user_input.lower() == 'exit':
        break

    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )

    with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        event_handler=EventHandler()
    ) as stream:
        stream.until_done()


