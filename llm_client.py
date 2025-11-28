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
	"""Get a response from the LLM given system and user prompts."""
	response = _client.responses.create(
		model = MODEL,
		input = [
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		],	
	)
	return response

def chunk_list(items, chunk_size: int):
	"""Yield successive 'chunk_size'-sized chunks from a list."""
	for i in range(0, len(items), chunk_size):
		yield items[i:i + chunk_size]