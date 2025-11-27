import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_client() -> OpenAI:
	"""Return a shared OpenAI client instance."""
	return _client