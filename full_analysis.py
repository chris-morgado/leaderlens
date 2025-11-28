import json
from typing import List, Dict
import pandas as pd

from llm_client import get_response, chunk_list

def run_full_analysis(semester: str) -> Dict:
    """
    Read full session CSV, call the LLM for analysis,
    and return an overall summary. Returns a dict.
    """
    print(f"Finding full session data for semester {semester}...")
    df = pd.read_csv(f"data/full{semester}.csv")
    print(df.iloc[0])
    