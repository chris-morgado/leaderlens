import json
from typing import List, Dict
import pandas as pd

from llm_client import get_response, chunk_list

def run_peer_analysis(semester: str, chunk_size: int) -> Dict:
	"""
	Read peer observation CSV, chunk it, call the LLM for each chunk,
	and merge into a single overall summary. Returns a dict.
	"""
	print(f"Finding peer observation data for semester {semester}...")
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

	n = min(
		len(openers_acts_closers),
		len(interactions),
		len(improvements),
		len(did_wells),
		len(general_feedback),
	)
	openers_acts_closers = openers_acts_closers[:n]
	interactions = interactions[:n]
	improvements = improvements[:n]
	did_wells = did_wells[:n]
	general_feedback = general_feedback[:n]

	print(f"Total observations: {n}. Processing in chunks of {chunk_size}...")

	chunk_summaries: List[Dict] = []

	for chunk_indices in chunk_list(list(range(n)), chunk_size):
		o_chunk = [openers_acts_closers[i] for i in chunk_indices]
		inter_chunk = [interactions[i] for i in chunk_indices]
		imp_chunk = [improvements[i] for i in chunk_indices]
		well_chunk = [did_wells[i] for i in chunk_indices]
		fb_chunk = [general_feedback[i] for i in chunk_indices]

		print(f"- Analyzing chunk with {len(chunk_indices)} observations...")
		chunk_summary = analyze_peer_observations_chunk(
			o_chunk,
			inter_chunk,
			imp_chunk,
			well_chunk,
			fb_chunk,
		)
		chunk_summaries.append(chunk_summary)

	print("Merging chunk summaries into overall metrics...")
	overall_summary = merge_peer_observation_summaries(chunk_summaries)
	return overall_summary


def analyze_peer_observations_chunk(openers_acts_closers: List[str], interactions: List[str], improvements: List[str], did_wells: List[str], general_feedback: List[str]) -> Dict:
    """Analyze a chunk of peer observation comments and return a summary dict."""
    system_prompt = ANALYZE_CHUNK_SYSTEM_PROMPT
    user_prompt = get_chunk_user_prompt(openers_acts_closers, interactions, improvements, did_wells, general_feedback,)

    response = get_response(system_prompt, user_prompt)
    json_text = response.output[0].content[0].text
    return json.loads(json_text)


def merge_peer_observation_summaries(chunk_summaries: List[Dict]) -> Dict:
    """Merge multiple chunk summaries into a single overall summary dict."""
    system_prompt = MERGE_CHUNK_SYSTEM_PROMPT
    user_prompt = get_merge_chunk_user_prompt(chunk_summaries)

    response = get_response(system_prompt, user_prompt)
    json_text = response.output[0].content[0].text
    return json.loads(json_text)


ANALYZE_CHUNK_SYSTEM_PROMPT = (
		"You are helping a Supplemental Instruction program manager analyze "
		"peer observation forms for SI Leaders. You will be given lists of "
		"qualitative comments about different aspects of sessions. "
		"Use them to compute program-level metrics and summarize patterns."
	)

MERGE_CHUNK_SYSTEM_PROMPT = (
		"You are aggregating multiple partial analyses of SI peer observations. "
		"Each item in the list is a JSON summary computed for one subset (chunk) "
		"of the data. Your job is to combine them into a single overall summary."
	)

def get_merge_chunk_user_prompt(chunk_summaries: List[Dict]) -> str:
    return f"""
Here are the chunk-level summaries as a JSON list: {json.dumps(chunk_summaries, indent=2)}
Each item has this schema:
{{
  "openers_overall": "string",
  "activities_overall": "string",
  "closers_overall": "string",
  "approx_percent_doing_closers": "string",
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

Return your answer as JSON with this exact structure and NOTHING else:

{{
  "openers_overall": "string",
  "activities_overall": "string",
  "closers_overall": "string",
  "approx_percent_doing_closers": "string",
  "interaction_overall": "string",
  "common_improvements": ["string"],
  "common_strengths": ["string"],
  "common_red_flags": ["string"]
}}
"""

def get_chunk_user_prompt(openers_acts_closers: List[str], interactions: List[str], improvements: List[str], did_wells: List[str], general_feedback: List[str]) -> str:
    return f"""
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

Using ONLY the information in these comments, answer the following program-level questions. When showing percentages, just show (xx% are good):

- What percentage of openers are good? In one sentence, how are all the openers?
- What percentage of activities are good? In one sentence, how are all the activities?
- What percentage of closers are good? In one sentence, how are all the closers? 
- What percentage of SILs are doing closers? 
- What percentage of SILs have good interactions with their students? How are most SILs interacting with their students?
- What could most people be improving on? (in list form with a count of how many mentioned each)
- What are most people doing well with? (in list form with a count of how many mentioned each)
- Most common red flags (if any), in list form?

Return your answer as JSON with this exact structure and NOTHING else:

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