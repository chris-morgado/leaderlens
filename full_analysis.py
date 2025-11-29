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
    df = df.rename(columns={
        "What class does the SI leader support?": "class_supported",
        "Is this a full observation or coaching session?": "session_type",
        
        # COACHING SESSION
        "What did you discuss with the SIL?": "discussion_with_sil",
        "If the SI Leader ran an activity for you, what were areas of strength and for improvement during that activity? (Please also put notes on these areas into their observation/self-reflection sheet.)": "activity_strengths_improvements",
        "Additional Comments:": "additional_comments",
        
        # FULL SESSION 
        # Session Requirements
        "Session Requirements: [Session plan utilized (as far as you can tell)]": "req_session_plan_utilized",
        "Session Requirements: [Agenda displayed/shared]": "req_agenda_displayed",
        "How was the session opened?": "session_open",
        "Which collaborative techniques did the SI Leader use during the session?": "collaborative_techniques",
        "Space use: what was the structure of the room and its purpose?": "space_use",
        "The SI Leader... [Uses a variety of collaborative techniques & learning activities]": "uses_varied_collab_techniques",
        "The SI Leader... [Uses activities that serve a broad range of learning styles (visual, auditory, kinesthetic)]": "uses_varied_learning_styles",
        "The SI Leader... [Includes or mentions study strategies or tips]": "includes_study_strategies",
        "The SI Leader... [Redirects a majority of questions (to a student, the group, or source materials)]": "redirects_questions",
        "The SI Leader... [Breaks down large concepts without re-lecturing]": "breaks_down_concepts",
        "The SI Leader... [Allows students to process question or prompt before providing insight (wait time)]": "uses_wait_time",
        "The SI Leader... [Consistently and effectively checks for understanding]": "checks_understanding",
        "The SI Leader... [Actively encourages student interactions by moving around the room, having students scribe, break-out groups, etc]": "encourages_interaction",
        "The SI Leader... [Makes sure information is correct]": "ensures_accuracy",
        "The SI Leader... [Balances having a productive and flexible session]": "balances_productivity_flexibility",
        "What are areas of improvement or strengths for the SIL from above?": "summary_strengths_improvements",
        # Session Atmosphere
        "Rate the SI Leader on the following: [Demonstrates respect for all students]": "rate_respect",
        "Rate the SI Leader on the following: [Makes an effort to connect with all students]": "rate_connection",
        "Rate the SI Leader on the following: [Fosters a comfortable learning environment for all students]": "rate_comfort_environment",
        "Rate the SI Leader on the following: [Praises & encourages students for their contributions]": "rate_praise",
        "Rate the SI Leader on the following: [Knows and uses the students' names]": "rate_uses_names",
        "Rate the SI Leader on the following: [Behaves in a professional manner throughout session]": "rate_professionalism",
        "Rate the SI Leader on the following: [Models excitement for the subject]": "rate_excited",
        "Rate the SI Leader on the following: [Greets and actively incorporates all students (including late comers) into the session activities]": "rate_includes_all_students",
        "Rate the SI Leader on the following: [Most people participated in the session]": "rate_participation",
        "Rate the SI Leader on the following: [Learning was student led (for example, SI participants hold the marker more than the SI Leader).]": "rate_student_led",
        "What are areas of improvement or strengths for the SIL from above?,": "summary_strengths_improvements_2",
        # Overall
        "How many students were present in the session?": "num_students_present",
        "How did the session close?": "session_close",
        "Overall areas of strength for SI Leader. (Please copy your answer below into the email you send to the SI Leader.)": "overall_strengths",
        "Overall areas of improvement for SI Leader.  (Please copy your answer below into the email you send to the SI Leader.)": "overall_improvements",
    })

    full_obs = (df["session_type"] == "Full observation").mean() * 100
    coaching_obs = (df["session_type"] == "Coaching session (i.e., no students have shown up in the first 15 minutes)").mean() * 100
    print(f"\nFull Observations:\t\t\t{coaching_obs:.2f}%\nCoaching Sessions:\t\t\t{full_obs:.2f}%\n")

    requirements_dict = dict()
    requirements_dict["Uses varied collab. tech.:\t\t"]      = get_percentage("uses_varied_collab_techniques", df)
    requirements_dict["Uses varied learning styles:\t\t"]    = get_percentage("uses_varied_learning_styles", df)
    requirements_dict["Includes study strategies:\t\t"]      = get_percentage("includes_study_strategies", df)
    requirements_dict["Redirects questions:\t\t\t"]          = get_percentage("redirects_questions", df)
    requirements_dict["Breaks down concepts:\t\t\t"]         = get_percentage("breaks_down_concepts", df)
    requirements_dict["Uses wait time:\t\t\t\t"]             = get_percentage("uses_wait_time", df)
    requirements_dict["Checks for understanding:\t\t"]       = get_percentage("checks_understanding", df)
    requirements_dict["Encourages interaction:\t\t\t"]       = get_percentage("encourages_interaction", df)
    requirements_dict["Ensures accuracy:\t\t\t"]             = get_percentage("ensures_accuracy", df)
    requirements_dict["Balances productivity/flex:\t\t"]     = get_percentage("balances_productivity_flexibility", df)
    print("Session Requirements:")
    for key, value in sorted(requirements_dict.items(), key=lambda item: item[1], reverse=True):
        print(f"{key} {value:.2f}% 'No' or 'Unsure'")

    atmosphere_dict = dict()
    atmosphere_dict["Demonstrates respect:\t\t\t"]          = get_percentage("rate_respect", df)
    atmosphere_dict["Connects with all students:\t\t"]      = get_percentage("rate_connection", df)
    atmosphere_dict["Fosters comfortable environment:\t"]   = get_percentage("rate_comfort_environment", df)
    atmosphere_dict["Praises & encourages:\t\t\t"]         = get_percentage("rate_praise", df)
    atmosphere_dict["Uses students' names:\t\t\t"]         = get_percentage("rate_uses_names", df)
    atmosphere_dict["Professional manner:\t\t\t"]          = get_percentage("rate_professionalism", df)
    atmosphere_dict["Models excitement:\t\t\t"]            = get_percentage("rate_excited", df)
    atmosphere_dict["Includes all students:\t\t\t"]       = get_percentage("rate_includes_all_students", df)
    atmosphere_dict["Most participated:\t\t\t"]            = get_percentage("rate_participation", df)
    atmosphere_dict["Learning was student led:\t\t"]      = get_percentage("rate_student_led", df)
    print("\nSession Atmosphere:") 
    for key, value in sorted(atmosphere_dict.items(), key=lambda item: item[1], reverse=True):
        print(f"{key} {value:.2f}% 'No' or 'Unsure'")
    

def get_percentage(key: str, df: pd.DataFrame):
    mask = df[key].isin(["No", "Unsure"])
    return mask.mean() * 100