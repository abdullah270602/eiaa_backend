import json
from openai import OpenAI
import os
from typing import Dict, List

from dotenv import load_dotenv

from app.services.file_utils import clean_json_response
from app.services.prompts import SYSTEM_PROMPT, SYSTEM_PROMPT_2

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com"),
)


def call_mapping_agent(
    template_columns: List[str],
    required_columns: List[str],
    uploaded_preview: Dict[str, List[str]],
    model_name="deepseek-chat",
) -> Dict:
    """ Calls the LLM agent to map uploaded columns to template columns."""
    try:
        user_prompt = (
            user_prompt
        ) = f"""
            Here are the template columns:
            {template_columns}

            Required columns:
            {required_columns}

            Uploaded file preview (column names and sample values):
            {uploaded_preview}
        """

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_2},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            stream=False,
        )

        content = response.choices[0].message.content
        print("🧪 Raw LLM Response:", json.dumps(content, indent=2))

        cleaned = clean_json_response(content)
        return json.loads(cleaned)
    except Exception as e:
        print(f"Error in call_mapping_agent: {str(e)}")
        import traceback; traceback.print_exc();
        raise Exception(f"Failed to process mapping request: {str(e)}")
