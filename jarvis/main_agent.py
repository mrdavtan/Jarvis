# main_agent.py
import os
import subprocess
from local_llm_function_calling import Generator
from llm_module import LLMModule
from semantic_router import Route, RouteLayer
from semantic_router.encoders import CohereEncoder, OpenAIEncoder

class MainAgent:
    def __init__(self, workspace_folder, model_name):
        self.workspace_folder = workspace_folder
        self.llm_module = LLMModule(model_name)
        self.llm_module.load_model()
        self.llm_module.load_pipelines()

        # Define the functions for the generator
        self.functions = [
            {
                "name": "list_workspace_contents",
                "description": "List the files and directories in the workspace folder",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
            {
                "name": "open_file_and_explain",
                "description": "Open a file in the workspace folder and explain its contents",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "The name of the file to open",
                        },
                    },
                    "required": ["file_name"],
                },
            },
            {
                "name": "execute_file_and_explain_output",
                "description": "Execute a Python file in the workspace folder and explain its output",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_name": {
                            "type": "string",
                            "description": "The name of the Python file to execute",
                        },
                    },
                    "required": ["file_name"],
                },
            },
        ]

        # Initialize the generator with the functions and the LLM model
        self.generator = Generator.hf(self.functions, self.llm_module.model)
        self.initialize_route_layer()

    def initialize_route_layer(self):
        routes = [
            Route(
                name="list_workspace_contents",
                utterances=[
                    "list the files in the workspace",
                    "show me the workspace contents",
                    "what files are in the workspace?",
                ],
                function_schema=self.functions[0],
            ),
            Route(
                name="open_file_and_explain",
                utterances=[
                    "explain the contents of {file_name}",
                    "open {file_name} and explain it",
                    "tell me about {file_name}",
                ],
                function_schema=self.functions[1],
            ),
            Route(
                name="execute_file_and_explain_output",
                utterances=[
                    "run {file_name} and explain the output",
                    "execute {file_name} and tell me what it does",
                    "what happens when I run {file_name}?",
                ],
                function_schema=self.functions[2],
            ),
        ]

        encoder = OpenAIEncoder()  # or CohereEncoder()
        self.route_layer = RouteLayer(encoder=encoder, routes=routes)

    def process_user_request(self, request):
        route_choice = self.route_layer(request)

        if route_choice.name == "list_workspace_contents":
            return self.list_workspace_contents()
        elif route_choice.name == "open_file_and_explain":
            file_name = route_choice.function_call["parameters"]["file_name"]
            return self.open_file_and_explain(file_name)
        elif route_choice.name == "execute_file_and_explain_output":
            file_name = route_choice.function_call["parameters"]["file_name"]
            return self.execute_file_and_explain_output(file_name)
        else:
            return "I apologize, but I don't know how to handle that request."

    def list_workspace_contents(self):
        try:
            contents = os.listdir(self.workspace_folder)
            response = "The workspace folder contains the following files and directories:\n"
            for item in contents:
                response += f"- {item}\n"
            return response.strip()
        except FileNotFoundError:
            return f"Sorry, the workspace folder '{self.workspace_folder}' does not exist."
        except Exception as e:
            return f"An error occurred while listing the workspace contents:\n{e}"

    def open_file_and_explain(self, file_name):
        file_path = os.path.join(self.workspace_folder, file_name)

        if not os.path.exists(file_path):
            return f"Sorry, the file '{file_name}' does not exist in the workspace folder."

        try:
            with open(file_path, 'r') as file:
                content = file.read()

            prompt = f"Explain the contents of the following file:\n\n{content}\n\nExplanation:"
            explanation = self.llm_module.generate_text(prompt, task="response").strip()
            return explanation
        except Exception as e:
            return f"An error occurred while opening and explaining the file:\n{e}"

    def execute_file_and_explain_output(self, file_name):
        file_path = os.path.join(self.workspace_folder, file_name)

        if not os.path.exists(file_path):
            return f"Sorry, the file '{file_name}' does not exist in the workspace folder."

        try:
            output = subprocess.check_output(['python', file_path], universal_newlines=True)

            prompt = f"Explain the output of the executed Python file:\n\n{output}\n\nExplanation:"
            explanation = self.llm_module.generate_text(prompt, task="response").strip()
            return explanation
        except subprocess.CalledProcessError as e:
            return f"An error occurred while executing the file:\n{e}"
        except Exception as e:
            return f"An error occurred while explaining the file output:\n{e}"

if __name__ == '__main__':
    workspace_folder = './workspace'
    model_name = 'mistralai/Mistral-7B-Instruct-v0.1'

    main_agent = MainAgent(workspace_folder, model_name)

    while True:
        user_request = input("User: ")
        response = main_agent.process_user_request(user_request)
        print("Assistant:", response)
