from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
from typing import List, Dict, Any
import logging


router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/",)
async def upload(file: UploadFile = File(...)):
    logging.info(f"Uploading file {file.filename}")
    try:
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = None

        if file.filename:
            filename_lower = file.filename.lower()

            for ext in allowed_extensions:
                if filename_lower.endswith(ext):
                    file_extension = ext
                    break

        if not file_extension:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type. Allowed types: {', '.join(allowed_extensions)}"
            )
            

        if file_extension == '.csv':
            response = "CSV"
        else:
            response = "XLS"
            
        return JSONResponse(content=response)
    
    except HTTPException:
        raise

    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")