import json
from fastapi import APIRouter, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
import io

from app.services.file_utils import extract_preview_data
from app.services.processing_service import UnifiedProcessingService


router = APIRouter(prefix="/upload", tags=["Upload"])

# Initialize the unified processing service
processing_service = UnifiedProcessingService()


def detect_extension(filename: str) -> str:
    if filename.endswith(".csv"):
        return ".csv"
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        return ".xlsx"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


@router.post(
    "/",
    status_code=200,
    summary="Upload and Process File",
    description="""
    Upload a CSV or Excel file and automatically detect template type (Customer, Product, Audit Trail, Supplier, Nominal Record, or Stock Transactions).
    The Agent will map columns to the appropriate Sage 50 template format.
    
    Supported file types: CSV (.csv), Excel (.xlsx, .xls)

    Template types:
        - customer: Customer/Account records
        - product: Product/Stock records
        - audit_trail: Audit Trail Transaction records
        - supplier: Supplier/Vendor records
        - nominal_record: Nominal Account records
        - stock_transactions: Stock Transaction/Movement records

    Response: Formatted file with processing metadata in headers
    """,
)
async def upload_and_format(
    file: UploadFile = File(
        ...,
        description="Upload CSV or Excel file for processing",
        media_type="multipart/form-data",
    ),
    force_template: Optional[str] = Query(
        None,
        description="Manual Selection (Optional): 'customer', 'product', 'audit_trail', 'supplier', 'nominal_record', or 'stock_transactions'",
        enum=["customer", "product", "audit_trail", "supplier", "nominal_record", "stock_transactions"],
    ),
):
    """
    Upload and format a file using automatic template detection or forced template type
    """
    extension = detect_extension(file.filename)
    contents = await file.read()
    buffer = io.BytesIO(contents)

    try:
        # Extract preview data and full DataFrame
        preview_data, df = extract_preview_data(buffer, extension)

        # Process using unified service
        if force_template:
            df_final, result_metadata = processing_service.force_template_processing(
                df, preview_data, force_template
            )
        else:
            df_final, result_metadata = processing_service.process_file(
                df, preview_data
            )

        # Convert to same format as input
        if extension == ".csv":
            # Return as CSV
            output_buffer = io.StringIO()
            df_final.to_csv(output_buffer, index=False)
            output_buffer.seek(0)
            media_type = "text/csv"
            output_stream = output_buffer
        else:
            # Return as Excel
            output_buffer = io.BytesIO()
            df_final.to_excel(output_buffer, index=False, engine="openpyxl")
            output_buffer.seek(0)
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            output_stream = output_buffer

        # Send complete metadata as header
        metadata_json = json.dumps(result_metadata)
        headers = {
            "Content-Disposition": f"attachment; filename=formatted_{file.filename}",
            "X-Processing-Result": metadata_json,
            "X-Template-Type": result_metadata["template_type"],
            "X-Template-Confidence": str(
                result_metadata["template_detection"]["confidence"]
            ),
        }

        return StreamingResponse(output_stream, media_type=media_type, headers=headers)

    except Exception as e:
        import traceback

        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get(
    "/templates",
    summary="Get Available Templates",
    description="Get information about all available template types and their configurations"
)
async def get_available_templates():
    """
    Get information about all available templates
    """
    try:
        templates_info = processing_service.get_available_templates()
        return JSONResponse(
            status_code=200,
            content={
                "available_templates": templates_info,
                "supported_force_template_values": list(templates_info.keys()),
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
