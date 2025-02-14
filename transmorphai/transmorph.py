import json
import xml.etree.ElementTree as ET
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class TransmorphAI:
    def __init__(self, schema, api_key, model="gpt-3.5-turbo-16k"):
        """
        Initializes TransmorphAI with a target data schema, an OpenAI API Key, and an optional model selection.
        :param schema: Dictionary defining the expected final format.
        :param api_key: OpenAI API Key provided by the user.
        :param model: OpenAI model to use (default: gpt-3.5-turbo-16k).
        """
        self.schema = schema
        self.api_key = api_key
        self.model = model
        openai.api_key = api_key

    def parse_input(self, data):
        """
        Converts the input into a Python dictionary, regardless of its format.
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
        """
        parsed_data = self.parse_input(data)
        
        prompt = (
            f"""
            You are an AI data transformer for APIs.
            
            1. Receive input in any format (JSON, XML, plain text) and convert it into structured JSON.
            2. Validate the data against the defined schema, ensuring all required fields are present.
            3. Maintain the correct data types: numbers as integers or floats, text as strings, and lists as arrays.
            4. Do not add any additional data or interpret beyond strict conversion.
            5. If required fields are missing, return an error with the list of missing fields.
            6. Detect the input language and keep the output format intact.
            7. Return only valid JSON output with no additional text.

            ### Expected Schema:
            {self.schema}

            ### Input Data:
            {parsed_data}
            """
        )
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,  # Use the selected model
                messages=[
                    {"role": "system", "content": "You are an API data validator and formatter. Only return properly structured JSON."},
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

# Example usage
def example():
    schema = {
        "name": "string",
        "age": "integer",
        "email": "string"
    }
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: You must provide an OpenAI API Key.")
        return
    
    # User can choose a different model, or it defaults to gpt-3.5-turbo-16k
    transmorph = TransmorphAI(schema, api_key, model="gpt-4")
    
    input_data = "<user><name>John</name><age>30</age><email>john@example.com</email></user>"
    
    result = transmorph.format_data(input_data)
    print(result)

if __name__ == "__main__":
    example()
