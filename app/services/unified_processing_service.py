from typing import Dict, List, Tuple
import pandas as pd

from app.services.template_manager import TemplateManager, TemplateType
from app.services.template_detection_agent import TemplateDetectionAgent
from app.services.dynamic_mapping_agent import DynamicMappingAgent
from app.services.formatter import apply_column_mapping

class UnifiedProcessingService:
    """
    Unified service that handles the complete workflow:
    1. Template detection
    2. Column mapping
    3. Data formatting
    """
    
    def __init__(self, templates_dir: str = None):
        self.template_manager = TemplateManager(templates_dir)
        self.detection_agent = TemplateDetectionAgent(self.template_manager)
        self.mapping_agent = DynamicMappingAgent(self.template_manager)
    
    def process_file(
        self, 
        df: pd.DataFrame, 
        preview_data: Dict[str, List[str]],
        force_template_type: TemplateType = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Complete processing workflow for uploaded files
        
        Args:
            df: The full DataFrame from uploaded file
            preview_data: Sample data for analysis
            force_template_type: Optional - force a specific template type
            
        Returns:
            Tuple of (formatted_dataframe, processing_result_metadata)
        """
        try:
            # Step 1: Template Detection (unless forced)
            if force_template_type:
                detected_template = force_template_type
                confidence = 1.0
                detection_method = "user selection (forced)"
            else:
                detected_template, confidence = self.detection_agent.detect_template_type(preview_data)
                detection_method = "auto"
            
            print(f"🔍 Template Detection: {detected_template.value} (confidence: {confidence:.2f})")
            
            # Step 2: Column Mapping
            mapping_result = self.mapping_agent.map_columns(
                detected_template, 
                preview_data
            )
            
            print(f"🗺️ Column Mapping: {len(mapping_result.get('column_mapping', {}))} columns mapped")
            
            # Step 3: Apply Formatting
            formatted_df = apply_column_mapping(
                df,
                mapping_result["column_mapping"],
                mapping_result.get("unmatched_columns", [])
            )
            
            # Step 4: Build comprehensive result metadata
            result_metadata = {
                "template_detection": {
                    "detected_type": detected_template.value,
                    "confidence": confidence,
                    "method": detection_method
                },
                "column_mapping": mapping_result["column_mapping"],
                "missing_required": mapping_result.get("missing_required", []),
                "unmatched_columns": mapping_result.get("unmatched_columns", []),
                "template_type": detected_template.value,
                "template_name": mapping_result.get("template_name", ""),
                "processing_summary": {
                    "total_columns_uploaded": len(preview_data),
                    "columns_mapped": len(mapping_result["column_mapping"]),
                    "columns_unmatched": len(mapping_result.get("unmatched_columns", [])),
                    "missing_required_fields": len(mapping_result.get("missing_required", [])),
                    "final_column_count": len(formatted_df.columns)
                }
            }
            
            return formatted_df, result_metadata
            
        except Exception as e:
            print(f"Error in unified processing: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to process file: {str(e)}")
    
    def get_available_templates(self) -> Dict[str, Dict]:
        """Get information about all available templates"""
        templates_info = {}
        for template_type, config in self.template_manager.get_all_templates().items():
            templates_info[template_type.value] = {
                "name": config.name,
                "description": config.description,
                "required_columns": config.required_columns,
                "file_path": config.file_path
            }
        return templates_info
    
    def force_template_processing(
        self,
        df: pd.DataFrame,
        preview_data: Dict[str, List[str]],
        template_type_str: str
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Process file with a specific template type (bypassing detection)
        
        Args:
            df: The full DataFrame
            preview_data: Sample data
            template_type_str: Template type as string ("customer", "product", "audit_trail", "supplier", "nominal_record")
        """
        template_type_map = {
            "customer": TemplateType.CUSTOMER,
            "product": TemplateType.PRODUCT,
            "audit_trail": TemplateType.AUDIT_TRAIL,
            "supplier": TemplateType.SUPPLIER,
            "nominal_record": TemplateType.NOMINAL_RECORD
        }
        
        if template_type_str.lower() not in template_type_map:
            raise ValueError(f"Unknown template type: {template_type_str}")
        
        template_type = template_type_map[template_type_str.lower()]
        
        return self.process_file(
            df, 
            preview_data, 
            force_template_type=template_type
        )
