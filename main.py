from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Body
from pydantic import BaseModel
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from spelling_correction import correct_spelling, suggest_alternatives
import uvicorn

app = FastAPI()

# === CORS Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === In-memory DB simulation ===
DB = {"raw": [], "final": []}
# Global variable to hold the last corrected list
LAST_PROCESSED_LIST: List[str] = []

# === Pydantic Models ===
class FinalList(BaseModel):
    final_items: List[str]

# === Helper: Read file content into list ===
async def read_file(file: UploadFile) -> List[str]:
    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = content.decode("latin-1")
        except:
            raise HTTPException(status_code=400, detail="Unable to decode file. Use UTF-8 or Latin-1.")

    # Split lines and remove empty
    return [line.strip() for line in text.splitlines() if line.strip()]

# ------------------------------
# Home route
# ------------------------------

@app.get("/")
def home():
    return {"message": "API is running."}


# === Endpoint: Process list (file + manual text) ===
@app.post("/process-list")
async def process_list(
    file: Optional[UploadFile] = File(None),
    text_input: Optional[str] = Form(None),
    json_input: Optional[List[str]] = Body(None)
):
    input_items = []

    # Process file if uploaded
    if file:
        if not file.filename.endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt files are allowed")
        input_items.extend(await read_file(file))

    # Process manual text input
    if text_input:
        for line in text_input.splitlines():
            if ',' in line:
                input_items.extend([item.strip() for item in line.split(',') if item.strip()])
            else:
                if line.strip():
                    input_items.append(line.strip())
    
    if json_input:
        input_items.extend([item.strip() for item in json_input if item.strip()])
    
    # No input provided
    if not input_items:
        raise HTTPException(status_code=400, detail="No valid items provided")

    # === Spelling correction ===
    corrected_list = []
    corrections_info = []

    for item in input_items:
        corrected_result = correct_spelling(item)
        if corrected_result["corrected"]:
            corrected_list.append(corrected_result["corrected"])
            corrections_info.append({
                "input": item,
                "corrected": corrected_result["corrected"],
                "alternatives": corrected_result["alternatives"]
            })
        else:
            alternatives = suggest_alternatives(item)
            corrections_info.append({
                "input": item,
                "corrected": None,
                "alternatives": alternatives
            })

    # Save raw input
    DB["raw"].append(input_items)
    # Save corrected list to global variable
    global LAST_PROCESSED_LIST
    LAST_PROCESSED_LIST = corrected_list

    return {
        "corrected_items": corrected_list,
        "details": corrections_info,
    }

# === Endpoint: Finalize list ===
@app.post("/finalize-list")
def finalize_list(data: Optional[FinalList] = None):
    global LAST_PROCESSED_LIST

    # If client provided data, use it
    if data and data.final_items:
        final_items = data.final_items
    # Otherwise, use last processed list
    elif LAST_PROCESSED_LIST:
        final_items = LAST_PROCESSED_LIST
    else:
        return {"status": "fail", "message": "No data available to finalize"}

    # Save to DB
    DB["final"].append(final_items)
    return {"status": "success", "message": f"Finalized list with {len(final_items)} items"}

import os 
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


# http://127.0.0.1:8000/process-list