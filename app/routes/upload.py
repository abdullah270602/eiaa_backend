import json
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Tuple
import os
import io
import pandas as pd

from app.services.file_utils import extract_preview_data
from app.services.formatter import apply_column_mapping
from app.services.llm_agent import call_mapping_agent
from app.services.template_loader import get_required_columns, load_template_columns


router = APIRouter(prefix="/upload", tags=["Upload"])

TEMPLATE_PATH = "templates\Customer Template.csv"

def detect_extension(filename: str) -> str:
    if filename.endswith(".csv"):
        return ".csv"
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        return ".xlsx"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


@router.post("/", status_code=200)
async def upload_and_format(file: UploadFile = File(...)):
    extension = detect_extension(file.filename)
    contents = await file.read()
    buffer = io.BytesIO(contents)

    try:
        preview_data, df = extract_preview_data(buffer, extension)
        template_columns = load_template_columns(TEMPLATE_PATH)
        required_columns = get_required_columns()

        mapping_result = call_mapping_agent(
            template_columns, required_columns, preview_data
        )

        df_final = apply_column_mapping(
            df, 
            mapping_result["column_mapping"],
            mapping_result["unmatched_columns"]
        )

        output_buffer = io.StringIO()
        df_final.to_csv(output_buffer, index=False)
        output_buffer.seek(0)

        # Send mapping result as a header (URL-safe)
        mapping_json = json.dumps(mapping_result)
        headers = {
            "Content-Disposition": f"attachment; filename=formatted_{file.filename}",
            "X-Mapping-Result": mapping_json
        }

        return StreamingResponse(
            output_buffer,
            media_type="text/csv",
            headers=headers
        )

    except Exception as e:
        import traceback; traceback.print_exc();
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
