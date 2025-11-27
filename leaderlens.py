import os
import json
from openai import OpenAI
import pandas as pd 
import typer
from dotenv import load_dotenv
load_dotenv()

app = typer.Typer()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chunk_list(items, chunk_size: int):
    """Yield successive 'chunk_size'-sized chunks from a list."""
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]

@app.command()
def peer(semester: str = "2251", chunk_size: int=10):
    try:
        print(f"Finding peer observation data...")
        df = pd.read_csv(f"data/peer{semester}.csv")

        df = df.rename(columns={
            "What are your thoughts about the opener, activities, and closer?": "opener_activities_closer",
            "Describe how the SI Leader interacted with the students. How did they foster a comfortable and productive learning environment? ": "interaction",
            "Describe one thing the SI Leader could work on improving?": "improvement",
            "Describe one thing the SI Leader did very well.": "did_well",
            "What general feedback would you like to share with the SI Leader?": "general_feedback",
        })
        
        openers_acts_closers = df["opener_activities_closer"].dropna().astype(str).tolist()
        interactions = df["interaction"].dropna().astype(str).tolist()
        improvements = df["improvement"].dropna().astype(str).tolist()
        did_wells = df["did_well"].dropna().astype(str).tolist()
        general_feedback = df["general_feedback"].dropna().astype(str).tolist()

        # makes sure all lists are the same length (in case some columns have extra NAs)
        n = min(len(openers_acts_closers), len(interactions), len(improvements), len(did_wells), len(general_feedback))
        openers_acts_closers = openers_acts_closers[:n]
        interactions = interactions[:n]
        improvements = improvements[:n]
        did_wells = did_wells[:n]
        general_feedback = general_feedback[:n]
        chunk_summaries: list[dict] = []

        print(f"Total observations: {n}. Processing in chunks of {chunk_size}...")

        for chunk_indices in chunk_list(list(range(n)), chunk_size):
            o_chunk = [openers_acts_closers[i] for i in chunk_indices]
            inter_chunk = [interactions[i] for i in chunk_indices]
            imp_chunk = [improvements[i] for i in chunk_indices]
            well_chunk = [did_wells[i] for i in chunk_indices]
            fb_chunk = [general_feedback[i] for i in chunk_indices]

            print(f"- Analyzing chunk with {len(chunk_indices)} observations...")
            chunk_summary = analyze_peer_observations_chunk(o_chunk, inter_chunk, imp_chunk, well_chunk, fb_chunk)
            chunk_summaries.append(chunk_summary)

        print("merging chunk summaries into overall metrics...")
        overall_summary = merge_peer_observation_summaries(chunk_summaries)
        print(json.dumps(overall_summary, indent=2, ensure_ascii=False))

    except FileNotFoundError:
        print("Data not found.")

def analyze_peer_observations_chunk(
	openers_acts_closers: list[str],
	interactions: list[str],
	improvements: list[str],
	did_wells: list[str],
	general_feedback: list[str],
):
	system_prompt = (
		"You are helping a Supplemental Instruction program manager analyze "
		"peer observation forms for SI Leaders. You will be given lists of "
		"qualitative comments about different aspects of sessions. "
		"Use them to compute program-level metrics and summarize patterns."
	)

	user_prompt = f"""
You are given peer observation comments from SI sessions.

### DATA

1) Opener / activities / closer comments:
{openers_acts_closers}

2) Interaction comments (how SI Leaders interact with students):
{interactions}

3) Improvement comments (one thing they could improve):
{improvements}

4) Did well comments (one thing they did very well):
{did_wells}

5) General feedback comments:
{general_feedback}

### TASKS

Using ONLY the information in these comments, answer the following program-level questions:

- How are all the openers?
- How are all the activities?
- How are all the closers? 
- What percentage of SILs are doing openers? (give a rough estimate based on the comments you see)
- How are most SILs interacting with their students?
- What could most people be improving on?
- What are most people doing well with?
- Most common red flags (if any)?

Return your answer as **JSON** with this exact structure and NOTHING else:

{{
  "openers_overall": "string",
  "activities_overall": "string",
  "closers_overall": "string",
  "approx_percent_doing_openers": "string",  // e.g. "around 80%"
  "interaction_overall": "string",
  "common_improvements": ["string", "string"],
  "common_strengths": ["string", "string"],
  "common_red_flags": ["string", "string"]
}}
"""

	response = client.responses.create(
		model="gpt-4.1-mini",
		input=[
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": user_prompt},
		]
    )

	json_text = response.output[0].content[0].text
	return json.loads(json_text)

def merge_peer_observation_summaries(chunk_summaries: list[dict]) -> dict:
    """
    merges chunk-level peer observation summaries into a single overall summary
    """

    system_prompt = (
        "You are aggregating multiple partial analyses of SI peer observations. "
        "Each item in the list is a JSON summary computed for one subset (chunk) "
        "of the data. Your job is to combine them into a single overall summary."
    )

    user_prompt = f"""
Here are the chunk-level summaries as a JSON list:

{json.dumps(chunk_summaries, indent=2)}

Each item has this schema:
{{
  "openers_overall": "string",
  "activities_overall": "string",
  "closers_overall": "string",
  "approx_percent_doing_openers": "string",
  "interaction_overall": "string",
  "common_improvements": ["string"],
  "common_strengths": ["string"],
  "common_red_flags": ["string"]
}}

### TASK

Combine all of these into ONE overall summary with the SAME schema. 
Reconcile differences by:
- capturing patterns that show up across many chunks,
- smoothing out percentages into a single rough estimate,
- merging and deduplicating similar strengths/improvements/red flags.

Return your answer as **JSON** with this exact structure and NOTHING else:

{{
  "openers_overall": "string",
  "activities_overall": "string",
  "closers_overall": "string",
  "approx_percent_doing_openers": "string",
  "interaction_overall": "string",
  "common_improvements": ["string"],
  "common_strengths": ["string"],
  "common_red_flags": ["string"]
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    json_text = response.output[0].content[0].text
    return json.loads(json_text)

@app.command()
def full(semester: str = "2251"):
    print(f"Finding full observation data...")
    print(f"right now using this for rate limit finds.. Limit Info:")

    limit_info = client.api_limits()
    print(limit_info)

@app.command()
def walkthrough(semester: str = "2251"):
    print(f"Finding walkthrough observation data...")
    
if __name__ == "__main__":
    app()