import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from jsonschema import ValidationError, validate
from openai import OpenAI

from semantic_router import Route, RouteLayer
from semantic_router.encoders import OpenAIEncoder
from semantic_router.schema import Message

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)


class OpenAILLM:
    def __init__(
        self,
        api_key: str = None,
        function_routes: List[Route] = None,
        encoder: OpenAIEncoder = None,
    ):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)

        print("API KEY: ", api_key)
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable or provide the API key as an argument."
            )

        self.client = OpenAI(api_key=api_key)

        if function_routes is None:
            function_routes = []

        if encoder is None:
            self.encoder = OpenAIEncoder()
        else:
            self.encoder = encoder

        self.route_layer = RouteLayer(encoder=self.encoder, routes=function_routes)

    def generate_text(self, messages: List[Dict], task: str = "response") -> str:
        try:
            print(f"OpenAILLM: Sending request to OpenAI API with messages: {messages}")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
            )
            print(f"OpenAILLM: Received response from OpenAI API: {response}")
            return response.choices[0].message.content.strip()
        except Exception as e:
            print("OpenAILLM: Error in generate_text:")
            print(str(e))
            raise e

    def extract_function_inputs(
        self, query: str, function_schema: Dict[str, Any]
    ) -> Dict[str, Any]:
        try:
            print(f"OpenAILLM: Extracting function inputs for query: {query}")
            print(f"OpenAILLM: Function schema: {function_schema}")

            prompt = f"""
            You are an AI assistant designed to extract input parameters from user queries based on a provided function schema.

            Function Schema:
            {json.dumps(function_schema, indent=2)}

            User Query:
            {query}

            Extract the input parameters from the user query and return them as a JSON object with the following format:
            {{
                "parameter_name_1": "parameter_value_1",
                "parameter_name_2": "parameter_value_2",
                ...
            }}

            If a parameter is not provided in the user query or is not defined in the function schema, omit it from the JSON object. Ensure that the parameter names exactly match those defined in the function schema.

            Extracted Inputs:
            """

            print(f"OpenAILLM: Sending request to OpenAI API with prompt: {prompt}")
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant designed to extract input parameters from user queries based on a provided function schema.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            print(f"OpenAILLM: Received response from OpenAI API: {response}")

            extracted_inputs_str = response.choices[0].message.content.strip()
            print(f"OpenAILLM: Extracted inputs string: {extracted_inputs_str}")
            try:
                if extracted_inputs_str:
                    extracted_inputs = json.loads(extracted_inputs_str)
                else:
                    extracted_inputs = {}
                print(f"OpenAILLM: Extracted inputs (before validation): {extracted_inputs}")

                # Validate the extracted inputs against the function schema
                validate(extracted_inputs, function_schema["parameters"])
                print(f"OpenAILLM: Extracted inputs (after validation): {extracted_inputs}")
                return extracted_inputs
            except (json.JSONDecodeError, ValidationError) as e:
                print("OpenAILLM: Error parsing or validating extracted inputs:")
                if isinstance(e, ValidationError):
                    error_details = e.message
                    print(f"Validation error details: {error_details}")
                else:
                    print(str(e))
                print("OpenAILLM: Extracted inputs string:")
                print(extracted_inputs_str)
                return {}  # Return an empty dictionary if extraction fails
        except Exception as e:
            print("OpenAILLM: Error in extract_function_inputs:")
            print(str(e))
            raise e
