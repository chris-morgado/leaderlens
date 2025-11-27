import pandas as pd 
import typer

app = typer.Typer()

@app.command()
def peer(semester: str = "2251"):
    try:
        print(f"Finding peer observation data...")
        df = pd.read_csv(f"data/peer{semester}.csv")
        print(df.iloc[78])
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