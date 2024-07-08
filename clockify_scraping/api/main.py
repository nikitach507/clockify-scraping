from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date, datetime
from clockify_scraping.config.settings import Settings
from clockify_scraping.sheet_connect import GoogleSheetAPI
import uvicorn


app = FastAPI()

credentials_file_path = Settings.GOOGLE_SHEETS_CREDENTIALS_FILE
token_file_path = Settings.GOOGLE_OAUTH_TOKEN_FILE
sheet_api = GoogleSheetAPI(credentials_path=credentials_file_path, token_path=token_file_path, spreadsheet_id=Settings.SPREADSHEET_ID)

class ProjectRequest(BaseModel):
    project_name: str
    start_date: date
    end_date: date

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/projects/")
def create_project(project: ProjectRequest):
    try:
        update_google_sheets(project.project_name, project.start_date, project.end_date)
        return {"message": f"Data for project '{project.project_name}' updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def update_google_sheets(project_name: str, start_date: date, end_date: date):
    try:
        sheet_name = f"{project_name} [{start_date:%Y-%m-%d} / {end_date:%Y-%m-%d}]"

        data_to_write = [
            ["Time Slot", "User 1", "User 2", "User 3"],
            ["12:00 PM", "Work desc", "-", "-"],
            ["12:15 PM", "-", "Work desc", "-"],
            ["12:30 PM", "-", "-", "Work desc"]
        ]

        print(f"Writing data to sheet '{sheet_name}'")
        # sheet_api.write_data(sheet_name=sheet_name, range_name="A1:D4", data=data_to_write)
        
    except Exception as e:
        print(f"Error updating Google Sheets: {e}")
        raise

if __name__ == "__main__":
    uvicorn.run(app, host="10.0.0.134", port=8000)