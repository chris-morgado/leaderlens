import pandas as pd 
import typer

app = typer.Typer()

@app.command()
def peer(semester: str = "2251"):
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
        
        print(df.columns)

        first = df.iloc[0]
        size = 75
        print("\nFirst observation metrics:")
        print("Opener/Activities/Closer:", first["opener_activities_closer"][0:size], "...")
        print("Interaction:\t\t ", first["interaction"][0:size], "...")
        print("Improvement:\t\t ", first["improvement"][0:size], "...")
        print("Did well:\t\t ", first["did_well"][0:size], "...")
        print("General feedback:\t ", first["general_feedback"][0:size], "...")

    except FileNotFoundError:
        print("Data not found.")

@app.command()
def full(semester: str = "2251"):
    print(f"Finding full observation data...")

@app.command()
def walkthrough(semester: str = "2251"):
    print(f"Finding walkthrough observation data...")
    
if __name__ == "__main__":
    app()