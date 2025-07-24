import json
from openai import OpenAI
import os
from typing import Dict, List

from dotenv import load_dotenv

from app.services.file_utils import clean_json_response
from app.services.template_manager import TemplateManager, TemplateType

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com"),
)

class DynamicMappingAgent:
    """Agent that handles column mapping for different template types"""
    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self.model_name = "deepseek-chat"
    
    def map_columns(
        self,
        template_type: TemplateType,
        uploaded_preview: Dict[str, List[str]]
    ) -> Dict:
        """Map uploaded columns to the specified template type"""
        
        # Get template configuration
        config = self.template_manager.get_template_config(template_type)
        template_columns = self.template_manager.load_template_columns(template_type)
        required_columns = self.template_manager.get_required_columns(template_type)
        
        # Build template-specific system prompt
        system_prompt = self._build_mapping_system_prompt(
            template_type, template_columns, required_columns
        )
        
        user_prompt = f"""
        Here are the template columns:
        {template_columns}

        Required columns:
        {required_columns}

        Uploaded file preview (column names and sample values):
        {uploaded_preview}
        """
        
        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                stream=False,
            )

            content = response.choices[0].message.content

            cleaned = clean_json_response(content)
            result = json.loads(cleaned)
            
            # Add metadata about the detection
            result["template_type"] = template_type.value
            result["template_name"] = config.name
            
            return result
            
        except Exception as e:
            print(f"Error in column mapping for {template_type.value}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to process mapping request for {template_type.value}: {str(e)}")
    
    def _build_mapping_system_prompt(
        self, 
        template_type: TemplateType, 
        template_columns: List[str], 
        required_columns: List[str]
    ) -> str:
        """Build template-specific system prompt for column mapping"""
        
        base_prompt = """
        You are a smart data mapping assistant for accounting software (like Sage 50).

        Your job is to:
        - Match columns from the uploaded file to the most appropriate columns in the target template format.
        - Match **semantically** and not just literally.
        - Always prioritize useful matches over skipping.
        - Mark a column as unmatched **only** if there is truly no relevant match.
        - If a required field is missing from the uploaded data, include it under "missing_required".
        - Respond only with a valid JSON object. Do NOT include markdown or explanation.

        The output format MUST be:
        {
          "column_mapping": {
            "UploadedColumnName": "MappedTemplateColumn"
          },
          "missing_required": [ "..." ],
          "unmatched_columns": [ "..." ]
        }
        """
        
        if template_type == TemplateType.CUSTOMER:
            specific_examples = """
            
            ## Customer Template Mapping Examples:
            
            ### Contact Information
            - "Customer Name" → "Account Name"
            - "Company" → "Account Name"  
            - "Client" → "Account Name"
            - "Phone" → "Telephone Number"
            - "Phone No" → "Telephone Number"
            - "Mobile" → "Telephone Number"
            - "Contact" → "Contact Name"
            - "Email" → "EMail"
            - "Email Address" → "EMail"
            - "Website" → "WWW"
            - "Web" → "WWW"

            ### Address Fields
            - "Address" → "Street 1"
            - "Address 1" → "Street 1"
            - "Address 2" → "Street 2"
            - "City" → "Town"
            - "State" → "County"
            - "Zip" → "Postcode"
            - "Zip Code" → "Postcode"
            - "Postal Code" → "Postcode"

            ### Financial Fields
            - "Max Credit" → "Credit Limit"
            - "Credit Line" → "Credit Limit"
            - "Limit" → "Credit Limit"
            - "Payment Terms" → "Terms Text"
            - "Net Days" → "Due Days"
            - "Payment Days" → "Due Days"
            - "Discount %" → "Discount Rate"
            - "Discount Percent" → "Discount Rate"

            ### Business Details
            - "VAT Number" → "VAT Reg No"
            - "Tax ID" → "VAT Reg No"
            - "Reference" → "Account Reference"
            - "Customer ID" → "Account Reference"
            - "Account ID" → "Account Reference"
            - "Code" → "Account Reference"
            """
        
        elif template_type == TemplateType.PRODUCT:
            specific_examples = """
            
            ## Product Template Mapping Examples:
            
            ### Product Identification
            - "Product Code" → "Stock Code"
            - "Item Code" → "Stock Code"
            - "SKU" → "Stock Code"
            - "Code" → "Stock Code"
            - "Part Number" → "Stock Code"
            - "Product Name" → "Description"
            - "Item Name" → "Description"
            - "Product Description" → "Description"
            - "Item Description" → "Description"
            - "Name" → "Description"

            ### Pricing Fields
            - "Price" → "Sales Price"
            - "Selling Price" → "Sales Price"
            - "Retail Price" → "Sales Price"
            - "List Price" → "Sales Price"
            - "Purchase Price" → "Cost Price"
            - "Buy Price" → "Cost Price"
            - "Wholesale Price" → "Cost Price"
            - "Unit Cost" → "Cost Price"

            ### Inventory Fields
            - "Stock Level" → "Re-Order Level"
            - "Min Stock" → "Re-Order Level"
            - "Reorder Point" → "Re-Order Level"
            - "Quantity" → "Re-Order Quantity"
            - "Min Qty" → "Re-Order Quantity"
            - "UOM" → "Unit of Sale"
            - "Unit" → "Unit of Sale"
            - "Measure" → "Unit of Sale"

            ### Supplier Information
            - "Supplier Code" → "Supplier A/C Ref"
            - "Vendor Code" → "Supplier A/C Ref"
            - "Supplier ID" → "Supplier A/C Ref"
            - "Supplier Part" → "Supplier Part Ref"
            - "Vendor Part" → "Supplier Part Ref"
            - "Supplier SKU" → "Supplier Part Ref"

            ### Product Classification
            - "Category" → "Stock Category"
            - "Type" → "Stock Category"
            - "Group" → "Stock Category"
            - "Class" → "Stock Category"
            - "Barcode" → "Bar Code"
            - "UPC" → "Bar Code"
            - "EAN" → "Bar Code"
            
            ### Physical Properties
            - "Weight (kg)" → "Weight"
            - "Weight (lbs)" → "Weight"
            - "Mass" → "Weight"
            - "Item Weight" → "Weight"
            """
        
        elif template_type == TemplateType.AUDIT_TRAIL:
            specific_examples = """
            
            ## Audit Trail Template Mapping Examples:
            
            ### Transaction Identification
            - "Transaction Type" → "Type"
            - "Entry Type" → "Type"
            - "Record Type" → "Type"
            - "Account Code" → "Account Reference"
            - "Customer Code" → "Account Reference"
            - "Client Reference" → "Account Reference"
            - "Nominal Code" → "Nominal A/C Ref"
            - "GL Account" → "Nominal A/C Ref"
            - "General Ledger" → "Nominal A/C Ref"

            ### Financial Information
            - "Amount" → "Net Amount"
            - "Value" → "Net Amount"
            - "Transaction Amount" → "Net Amount"
            - "Net Value" → "Net Amount"
            - "VAT Code" → "Tax Code"
            - "Tax Type" → "Tax Code"
            - "Sales Tax Code" → "Tax Code"
            - "VAT Amount" → "Tax Amount"
            - "Tax Value" → "Tax Amount"
            - "Sales Tax" → "Tax Amount"

            ### Transaction Details
            - "Transaction Date" → "Date"
            - "Entry Date" → "Date"
            - "Posted Date" → "Date"
            - "Ref" → "Reference"
            - "Reference Number" → "Reference"
            - "Transaction Ref" → "Reference"
            - "Description" → "Details"
            - "Narrative" → "Details"
            - "Transaction Details" → "Details"
            - "Comments" → "Details"

            ### Additional Fields
            - "Rate" → "Exchange Rate"
            - "Currency Rate" → "Exchange Rate"
            - "FX Rate" → "Exchange Rate"
            - "Extra Ref" → "Extra Reference"
            - "Additional Reference" → "Extra Reference"
            - "User" → "User Name"
            - "Posted By" → "User Name"
            - "Created By" → "User Name"
            - "Project Code" → "Project Refn"
            - "Job Reference" → "Project Refn"
            - "Department" → "Department Code"
            - "Dept Code" → "Department Code"
            - "Cost Center" → "Cost Code Refn"
            - "Cost Centre" → "Cost Code Refn"
            """
        
        elif template_type == TemplateType.SUPPLIER:
            specific_examples = """
            
            ## Supplier Template Mapping Examples:
            
            ### Supplier Identification
            - "Supplier Code" → "Account Reference"
            - "Vendor Code" → "Account Reference"
            - "Supplier ID" → "Account Reference"
            - "Vendor ID" → "Account Reference"
            - "Supplier Name" → "Account Name"
            - "Vendor Name" → "Account Name"
            - "Company Name" → "Account Name"
            - "Business Name" → "Account Name"

            ### Contact Information
            - "Contact Person" → "Contact Name"
            - "Primary Contact" → "Contact Name"
            - "Main Contact" → "Contact Name"
            - "Phone" → "Telephone Number"
            - "Phone No" → "Telephone Number"
            - "Mobile" → "Telephone Number"
            - "Email" → "EMail"
            - "Email Address" → "EMail"
            - "Website" → "WWW"
            - "Web" → "WWW"

            ### Address Fields
            - "Address" → "Street 1"
            - "Address 1" → "Street 1"
            - "Address 2" → "Street 2"
            - "City" → "Town"
            - "State" → "County"
            - "Zip" → "Postcode"
            - "Zip Code" → "Postcode"
            - "Postal Code" → "Postcode"

            ### Financial Fields
            - "Max Credit" → "Credit Limit"
            - "Credit Line" → "Credit Limit"
            - "Payment Terms" → "Terms Text"
            - "Net Days" → "Due Days"
            - "Payment Days" → "Due Days"
            - "Discount %" → "Discount Rate"
            - "Discount Percent" → "Discount Rate"

            ### Business Details
            - "VAT Number" → "VAT Reg No"
            - "Tax ID" → "VAT Reg No"
            - "Reference" → "Account Reference"
            - "Code" → "Account Reference"
            - "Bank" → "Bank Name"
            - "Sort Code" → "Bank Sort Code"
            - "Account Number" → "Bank Account No"
            - "IBAN" → "Bank IBAN"
            - "Swift" → "Bank BIC Swift"
            - "BIC" → "Bank BIC Swift"
            """
        
        elif template_type == TemplateType.NOMINAL_RECORD:
            specific_examples = """
            
            ## Nominal Record Template Mapping Examples:
            
            ### Account Identification
            - "Account Code" → "Refn*"
            - "Code" → "Refn*"
            - "Reference" → "Refn*"
            - "Account Reference" → "Refn*"
            - "Nominal Code" → "Refn*"
            - "GL Code" → "Refn*"
            - "Account Name" → "Name"
            - "Description" → "Name"
            - "Account Description" → "Name"
            - "Title" → "Name"

            ### Budget Fields
            - "Annual Budget" → "Yearly Budget"
            - "Total Budget" → "Yearly Budget"
            - "Year Budget" → "Yearly Budget"
            - "Budget Amount" → "Yearly Budget"
            - "Jan Budget" → "Month 1 Budget"
            - "January" → "Month 1 Budget"
            - "Feb Budget" → "Month 2 Budget"
            - "February" → "Month 2 Budget"
            - "Mar Budget" → "Month 3 Budget"
            - "March" → "Month 3 Budget"
            - "Apr Budget" → "Month 4 Budget"
            - "April" → "Month 4 Budget"
            - "May Budget" → "Month 5 Budget"
            - "Jun Budget" → "Month 6 Budget"
            - "June" → "Month 6 Budget"
            - "Jul Budget" → "Month 7 Budget"
            - "July" → "Month 7 Budget"
            - "Aug Budget" → "Month 8 Budget"
            - "August" → "Month 8 Budget"
            - "Sep Budget" → "Month 9 Budget"
            - "September" → "Month 9 Budget"
            - "Oct Budget" → "Month 10 Budget"
            - "October" → "Month 10 Budget"
            - "Nov Budget" → "Month 11 Budget"
            - "November" → "Month 11 Budget"
            - "Dec Budget" → "Month 12 Budget"
            - "December" → "Month 12 Budget"

            ### Prior Year Fields
            - "Last Year Jan" → "Prior Year Month 1"
            - "Previous Year January" → "Prior Year Month 1"
            - "PY Jan" → "Prior Year Month 1"
            - "Last Year Feb" → "Prior Year Month 2"
            - "PY Feb" → "Prior Year Month 2"
            - "Last Year Dec" → "Prior Year Month 12"
            - "PY Dec" → "Prior Year Month 12"
            - "2 Years Ago Jan" → "Prior Yr2 Month 1"
            - "Yr-2 Jan" → "Prior Yr2 Month 1"
            - "3 Years Ago Jan" → "Prior Yr3 Month 1"
            - "Yr-3 Jan" → "Prior Yr3 Month 1"
            - "4 Years Ago Jan" → "Prior Yr4 Month 1"
            - "Yr-4 Jan" → "Prior Yr4 Month 1"
            - "5 Years Ago Jan" → "Prior Yr5 Month 1"
            - "Yr-5 Jan" → "Prior Yr5 Month 1"

            ### Quarterly Budget Fields
            - "Q1 Budget" → "Month 1 Budget" (use first month of quarter)
            - "Q2 Budget" → "Month 4 Budget"
            - "Q3 Budget" → "Month 7 Budget"
            - "Q4 Budget" → "Month 10 Budget"
            - "Quarter 1" → "Month 1 Budget"
            - "Quarter 2" → "Month 4 Budget"
            - "Quarter 3" → "Month 7 Budget"
            - "Quarter 4" → "Month 10 Budget"
            """
        
        else:
            specific_examples = ""
        
        return base_prompt + specific_examples
