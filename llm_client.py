import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = "gpt-4.1-mini"

def get_client() -> OpenAI:
	"""Return a shared OpenAI client instance."""
	return _client

def get_response(system_prompt: str, user_prompt: str) -> dict:
	response = _client.chat.completions.create(
		model=MODEL,
		input=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		],	)
	return response