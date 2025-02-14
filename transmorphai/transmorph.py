import json
import xml.etree.ElementTree as ET
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class TransmorphAI:
    def __init__(self, schema, api_key, model="gpt-4"):
        """
        Initializes TransmorphAI with a target schema, OpenAI API Key, and an optional model selection.
        :param schema: Dictionary defining the expected final format.
        :param api_key: OpenAI API Key provided by the user.
        :param model: OpenAI model to use (default: gpt-4).
        """
        self.schema = schema
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def parse_input(self, data):
        """
        Converts the input into a Python dictionary, regardless of its format.
        Supports JSON, XML, and plain text.
        """
        if isinstance(data, str):
            try:
                return json.loads(data)  # Attempt to parse JSON
            except json.JSONDecodeError:
                try:
                    root = ET.fromstring(data)  # Attempt to parse XML
                    return {child.tag: child.text for child in root}
                except ET.ParseError:
                    return {"raw_text": data}  # Plain text input
        return data  # Return as is if already a dictionary

    def format_data(self, data):
        """
        Formats the received data according to the defined schema.
        It will:
        - Detect the input language.
        - Map the received fields to the expected schema.
        - Convert data types as needed.
        - Ensure the correct output format.
        """
        parsed_data = self.parse_input(data)

        prompt = f"""
        You are an AI specializing in API data transformation.

        1️⃣ **Understand the data received**, even if it's in a different language or format.
        2️⃣ **Translate field names** to match the expected schema.
        3️⃣ **Correct data types** (e.g., convert strings to numbers if necessary).
        4️⃣ **Ensure output matches the required schema**.

        ### **Expected Schema:**
        {self.schema}

        ### **Received Data:**
        {parsed_data}

        🔹 **Your task:** Convert the received data to strictly match the expected schema, ensuring all required fields are present. If any field is missing, infer it based on the input.
        🔹 **Output only a valid JSON object following the schema.**
        """

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an advanced API data formatter. Always return structured JSON."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            formatted_data = response["choices"][0]["message"]["content"]
            return json.loads(formatted_data)
        except json.JSONDecodeError:
            return {"error": "OpenAI response is not valid JSON"}
        except openai.OpenAIError as e:
            return {"error": f"OpenAI API error: {str(e)}"}
        except Exception as e:
            return {"error": str(e)}
