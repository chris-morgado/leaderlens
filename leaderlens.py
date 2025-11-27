import json
import typer

from llm_client import get_client
from peer_analysis import run_peer_analysis

app = typer.Typer()
client = get_client()

CHUNK_SIZE = 10
SEMESTER = "2251"

@app.command()
def peer(semester: str = SEMESTER, chunk_size: int = CHUNK_SIZE):
	"""
	Run peer observation analysis for a given semester CSV.
	"""
	try:
		summary = run_peer_analysis(semester=semester, chunk_size=chunk_size)
		print(json.dumps(summary, indent=2, ensure_ascii=False))
	except FileNotFoundError:
		print("Data not found. Make sure data/peer<semester>.csv exists.")


@app.command()
def full(semester: str = SEMESTER):
	try:
		pass
	except FileNotFoundError:
		print("Data not found. Make sure data/full<semester>.csv exists.")

@app.command()
def walkthrough(semester: str = SEMESTER):
	try:
		pass
	except FileNotFoundError:
		print("Data not found. Make sure data/walkthrough<semester>.csv exists.")

if __name__ == "__main__":
	app()