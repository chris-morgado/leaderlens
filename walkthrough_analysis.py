import json
from typing import List, Dict
import pandas as pd

def run_walkthrough_analysis(semester: str) -> Dict:
    """
    Read walkthrough observation CSV, call the LLM for analysis,
    and return an overall summary. Returns a dict.
    """
    print(f"Finding walkthrough observation data for semester {semester}...")
    df = pd.read_csv(f"data/walkthrough{semester}.csv")
    print(df.iloc[0])