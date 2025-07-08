import time
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import io
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])

@router.post("/",)
async def upload(file: UploadFile = File(...)):
    logger.info(f" Uploading file {file.filename}")
    start = time.time()
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
        
        metadata = None
        
        if file_extension == '.csv':


            metadata = pd.read_csv(file.file, nrows=0)
            
            file.file.seek(0) # this a pointer to the beginning of the file
            row_count = sum(1 for _ in file.file) - 1  # Subtract header row
            file.file.seek(0)
            
            
        else: # xlsx or xls

            metadata = pd.read_excel(file.file, nrows=0)
            
            file.file.seek(0)
            df_full = pd.read_excel(file.file, usecols=[0])  # Only load 1 column
            row_count = df_full.shape[0]
            file.file.seek(0)
            
            
            
        end_time = round(time.time() - start, 2)
        columns = list(metadata.columns)
        # dtypes = metadata.dtypes.apply(lambda x: str(x)).to_dict()

        return JSONResponse(content={
            "filename": file.filename,
            "columns": columns,
            # "dtypes": dtypes,
            "num_rows": row_count,
            "time_taken": end_time
        })
    
    except HTTPException:
        raise

    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")