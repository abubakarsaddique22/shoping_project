from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from spell_checker import correct_spelling, suggest_alternatives

app = FastAPI()

# In-memory DB simulation
DB = {"raw": [], "final": []}


# === Request Models ===
class RawList(BaseModel):
    items: List[str]

class FinalList(BaseModel):
    final_items: List[str]


# === Endpoints ===
@app.post("/process-list")
def process_list(data: RawList):
    if not data.items:
        raise HTTPException(status_code=400, detail="Empty list provided")
    
    corrected_list = []
    corrections_info = []

    for item in data.items:
        corrected = correct_spelling(item)
        if corrected:
            corrected_list.append(corrected)
            corrections_info.append({"input": item, "corrected": corrected, "alternatives": []})
        else:
            corrections_info.append({"input": item, "corrected": None, "alternatives": suggest_alternatives(item)})

    DB["raw"].append(data.items)

    return {"corrected_items": corrected_list, "details": corrections_info}


@app.post("/finalize-list")
def finalize_list(data: FinalList):
    if not data.final_items:
        return {"status": "fail", "message": "Final list cannot be empty"}
    
    try:
        DB["final"].append(data.final_items)
        return {"status": "success"}
    except Exception as e:
        return {"status": "fail", "message": str(e)}
