import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import pandas as pd

class TemplateType(Enum):
    CUSTOMER = "customer"
    PRODUCT = "product"
    AUDIT_TRAIL = "audit_trail"
    SUPPLIER = "supplier"
    NOMINAL_RECORD = "nominal_record"

@dataclass
class TemplateConfig:
    name: str
    template_type: TemplateType
    file_path: str
    required_columns: List[str]
    key_indicators: List[str]  # Column names that strongly indicate this template type
    description: str

class TemplateManager:
    """Manages multiple templates and their configurations"""
    
    def __init__(self, templates_dir: str = None):
        self.templates_dir = templates_dir or os.path.join(os.getcwd(), "templates")
        self.templates: Dict[TemplateType, TemplateConfig] = {}
        self._initialize_templates()
    
    def _initialize_templates(self):
        """Initialize all available templates"""

        # Customer template configuration
        customer_config = TemplateConfig(
            name="Customer Template",
            template_type=TemplateType.CUSTOMER,
            file_path=os.path.join(self.templates_dir, "Customer Template.csv"),
            required_columns=["Account Reference"],
            key_indicators=[
                "account reference", "customer", "client", "account name", 
                "company", "contact name", "telephone", "email", "address",
                "credit limit", "payment terms", "vat", "postcode"
            ],
            description="Customer/Account records for Sage 50"
        )
        
        # Product template configuration
        product_config = TemplateConfig(
            name="Product Template",
            template_type=TemplateType.PRODUCT,
            file_path=os.path.join(self.templates_dir, "Product_Record_Template.csv"),
            required_columns=["Stock Code"],
            key_indicators=[
                "stock code", "product", "item", "description", "price", 
                "cost", "sales price", "cost price", "stock", "inventory",
                "bar code", "supplier", "category", "unit of sale"
            ],
            description="Product/Stock records for Sage 50"
        )
        
        # Audit Trail template configuration
        audit_trail_config = TemplateConfig(
            name="Audit Trail Template",
            template_type=TemplateType.AUDIT_TRAIL,
            file_path=os.path.join(self.templates_dir, "Audit_Trail_Transaction_template.csv"),
            required_columns=["Type", "Account Reference", "Nominal A/C Ref", "Date", "Net Amount", "Tax Code", "Tax Amount"],
            key_indicators=[
                "transaction", "audit", "type", "account reference", "nominal", 
                "date", "reference", "details", "net amount", "tax code", 
                "tax amount", "exchange rate", "user name", "project", "cost code"
            ],
            description="Audit Trail Transaction records for Sage 50"
        )
        
        # Supplier template configuration
        supplier_config = TemplateConfig(
            name="Supplier Template",
            template_type=TemplateType.SUPPLIER,
            file_path=os.path.join(self.templates_dir, "Supplier_Record_Template.csv"),
            required_columns=["Account Reference"],
            key_indicators=[
                "account reference", "supplier", "vendor", "account name", 
                "company", "contact name", "telephone", "email", "address",
                "credit limit", "payment terms", "vat", "postcode", "purchase"
            ],
            description="Supplier/Vendor records for Sage 50"
        )
        
        # Nominal Record template configuration
        nominal_config = TemplateConfig(
            name="Nominal Record Template",
            template_type=TemplateType.NOMINAL_RECORD,
            file_path=os.path.join(self.templates_dir, "Nominal_Record_Template.csv"),
            required_columns=["Refn*"],
            key_indicators=[
                "refn", "name", "budget", "month", "yearly budget", "prior year",
                "nominal", "account", "budget allocation", "financial", "ledger"
            ],
            description="Nominal Account records for Sage 50"
        )
        
        self.templates[TemplateType.CUSTOMER] = customer_config
        self.templates[TemplateType.PRODUCT] = product_config
        self.templates[TemplateType.AUDIT_TRAIL] = audit_trail_config
        self.templates[TemplateType.SUPPLIER] = supplier_config
        self.templates[TemplateType.NOMINAL_RECORD] = nominal_config
    
    def get_template_config(self, template_type: TemplateType) -> TemplateConfig:
        """Get configuration for a specific template type"""
        if template_type not in self.templates:
            raise ValueError(f"Template type {template_type.value} not found")
        return self.templates[template_type]
    
    def get_all_templates(self) -> Dict[TemplateType, TemplateConfig]:
        """Get all available template configurations"""
        return self.templates.copy()
    
    def load_template_columns(self, template_type: TemplateType) -> List[str]:
        """Load column names from a template file"""
        config = self.get_template_config(template_type)
        
        if not os.path.exists(config.file_path):
            raise FileNotFoundError(f"Template file not found at: {config.file_path}")
        
        try:
            df = pd.read_csv(config.file_path)
            return df.columns.tolist()
        except pd.errors.EmptyDataError:
            raise ValueError(f"Template file {config.file_path} is empty")
        except pd.errors.ParserError:
            raise ValueError(f"Invalid CSV format in template file {config.file_path}")
        except Exception as e:
            raise Exception(f"Error loading template file {config.file_path}: {str(e)}")
    
    def get_required_columns(self, template_type: TemplateType) -> List[str]:
        """Get required columns for a specific template type"""
        config = self.get_template_config(template_type)
        return config.required_columns.copy()
    
    def add_template(self, config: TemplateConfig):
        """Add a new template configuration"""
        self.templates[config.template_type] = config
