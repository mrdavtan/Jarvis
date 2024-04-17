# main_agent.py
import os
import subprocess
from openai_llm import OpenAILLM
from semantic_router import Route

class MainAgent:
    def __init__(self, workspace_folder):
        self.workspace_folder = workspace_folder

        # Define the function routes
        self.function_routes = [
            Route(
                name="list_workspace_contents",
                utterances=[
                    "list the files in the workspace",
                    "show me the workspace contents",
                    "what files are in the workspace?",
                ],
                function_schema={
                    "name": "list_workspace_contents",
                    "description": "List the files and directories in the workspace folder",
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
            ),
            Route(
                name="open_file_and_explain",
                utterances=[
                    "explain the contents of {file_name}",
                    "open {file_name} and explain it",
                    "tell me about {file_name}",
                ],
                function_schema={
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
            ),
            Route(
                name="execute_file_and_explain_output",
                utterances=[
                    "run {file_name} and explain the output",
                    "execute {file_name} and tell me what it does",
                    "what happens when I run {file_name}?",
                ],
                function_schema={
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
            ),
        ]

        # Initialize the OpenAILLM with the function routes
        self.llm = OpenAILLM(function_routes=self.function_routes)

    def process_user_request(self, request):
        print(f"MainAgent: Processing user request: {request}")
        # Extract function inputs using Semantic Router
        route_choice = self.llm.route_layer(request)
        print(f"MainAgent: Route choice: {route_choice}")

        if route_choice is None or route_choice.name is None:
            print("MainAgent: No matching route found.")
            return "I apologize, but I don't know how to handle that request."

        function_name = route_choice.name
        print(f"MainAgent: Function name: {function_name}")

        if function_name == "list_workspace_contents":
            return self.list_workspace_contents()
        elif function_name == "open_file_and_explain":
            file_name = route_choice.function_call.get("file_name")
            if file_name:
                print(f"MainAgent: File name: {file_name}")
                return self.open_file_and_explain(file_name)
            else:
                print("MainAgent: File name not provided.")
                return "Please provide a valid file name."
        elif function_name == "execute_file_and_explain_output":
            file_name = route_choice.function_call.get("file_name")
            if file_name:
                print(f"MainAgent: File name: {file_name}")
                return self.execute_file_and_explain_output(file_name)
            else:
                print("MainAgent: File name not provided.")
                return "Please provide a valid file name."
        else:
            print("MainAgent: Unknown function name.")
            return "I apologize, but I don't know how to handle that request."

    def list_workspace_contents(self):
        try:
            print(f"MainAgent: Listing workspace contents in {self.workspace_folder}")
            contents = os.listdir(self.workspace_folder)
            response = "The workspace folder contains the following files and directories:\n"
            for item in contents:
                response += f"- {item}\n"
            return response.strip()
        except FileNotFoundError:
            print(f"MainAgent: Workspace folder not found: {self.workspace_folder}")
            return f"Sorry, the workspace folder '{self.workspace_folder}' does not exist."
        except Exception as e:
            print(f"MainAgent: Error listing workspace contents: {e}")
            return f"An error occurred while listing the workspace contents:\n{e}"

    def open_file_and_explain(self, file_name):
        file_path = os.path.join(self.workspace_folder, file_name)

        if not os.path.exists(file_path):
            print(f"MainAgent: File not found: {file_path}")
            return f"Sorry, the file '{file_name}' does not exist in the workspace folder."

        try:
            print(f"MainAgent: Opening file: {file_path}")
            with open(file_path, 'r') as file:
                content = file.read()

            print(f"MainAgent: Generating explanation for file: {file_name}")
            prompt = f"Explain the contents of the following file:\n\n{content}\n\nExplanation:"
            explanation = self.llm.generate_text([{"role": "system", "content": prompt}])
            return explanation.strip()
        except Exception as e:
            print(f"MainAgent: Error opening and explaining file: {e}")
            return f"An error occurred while opening and explaining the file:\n{e}"

    def execute_file_and_explain_output(self, file_name):
        file_path = os.path.join(self.workspace_folder, file_name)

        if not os.path.exists(file_path):
            print(f"MainAgent: File not found: {file_path}")
            return f"Sorry, the file '{file_name}' does not exist in the workspace folder."

        try:
            print(f"MainAgent: Executing file: {file_path}")
            output = subprocess.check_output(['python', file_path], universal_newlines=True)

            print(f"MainAgent: Generating explanation for file output: {file_name}")
            prompt = f"Explain the output of the executed Python file:\n\n{output}\n\nExplanation:"
            explanation = self.llm.generate_text([{"role": "system", "content": prompt}])
            return explanation.strip()
        except subprocess.CalledProcessError as e:
            print(f"MainAgent: Error executing file: {e}")
            return f"An error occurred while executing the file:\n{e}"
        except Exception as e:
            print(f"MainAgent: Error explaining file output: {e}")
            return f"An error occurred while explaining the file output:\n{e}"

if __name__ == '__main__':
    workspace_folder = './workspace'

    main_agent = MainAgent(workspace_folder)

    while True:
        user_request = input("User: ")
        response = main_agent.process_user_request(user_request)
        print("Assistant:", response)
