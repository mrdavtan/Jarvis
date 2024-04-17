# openai_llm.py
import os
import openai
from typing import Dict, List
from semantic_router import Route, RouteLayer
from semantic_router.encoders import OpenAIEncoder

class OpenAILLM:
    def __init__(self, api_key: str = None, function_routes: List[Route] = None):
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable or provide the API key as an argument.")
        openai.api_key = api_key

        if function_routes is None:
            function_routes = []

        self.encoder = OpenAIEncoder()
        self.route_layer = RouteLayer(encoder=self.encoder, routes=function_routes)

    def generate_text(self, messages: List[Dict], task: str = "response") -> str:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4-turbo-preview" for more advanced tasks
                messages=messages,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("Error:")
            print(str(e))
            raise e

    def extract_function_inputs(self, user_request: str) -> Dict:
        try:
            route_choice = self.route_layer(user_request)

            if route_choice is None:
                return {}

            function_schema = route_choice.function_schema
            prompt = f"Extract the input parameters for the following function from the user's request:\n\nFunction Schema:\n{function_schema}\n\nUser Request:\n{user_request}\n\nExtracted Inputs:"

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # or "gpt-4-turbo-preview" for more advanced tasks
                messages=[
                    {"role": "system", "content": "You are a helpful assistant designed to extract input parameters from user requests based on the provided function schema."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            extracted_inputs_str = response.choices[0].message.content.strip()
            extracted_inputs = eval(extracted_inputs_str)
            return extracted_inputs
        except Exception as e:
            print("Error:")
            print(str(e))
            raise e

if __name__ == "__main__":
    # Define function routes
    function_routes = [
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
        # Add more function routes as needed
    ]

    openai_llm = OpenAILLM(function_routes=function_routes)

    # Example usage
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Who won the world series in 2020?"},
    ]
    response = openai_llm.generate_text(messages)
    print(response)

    user_request = "explain the contents of example.py"
    extracted_inputs = openai_llm.extract_function_inputs(user_request)
    print(extracted_inputs)
