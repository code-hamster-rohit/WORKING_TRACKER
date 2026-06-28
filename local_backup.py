import json
from dotenv import load_dotenv
load_dotenv()
from db.rules import get_all

def main():
    print("Fetching all data from MongoDB...")
    workings = get_all("WORKING_TRACKER", "WORKING_DETAILS", {})
    
    if not workings:
        print("No data found in the database.")
        return

    # Convert ObjectId to string for JSON serialization
    for w in workings:
        w["_id"] = str(w["_id"])

    output_file = "local_db_backup.json"
    
    with open(output_file, "w") as f:
        json.dump(workings, f, indent=4)
        
    print(f"Successfully backed up {len(workings)} records to {output_file}")

if __name__ == "__main__":
    main()
