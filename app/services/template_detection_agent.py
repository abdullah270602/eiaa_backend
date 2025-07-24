import json
from openai import OpenAI
import os
from typing import Dict, List, Tuple
from dotenv import load_dotenv

from app.services.file_utils import clean_json_response
from app.services.template_manager import TemplateManager, TemplateType, TemplateConfig

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_API_BASE_URL", "https://api.deepseek.com"),
)

class TemplateDetectionAgent:
    """Agent responsible for detecting which template type the uploaded data belongs to"""
    
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self.model_name = "deepseek-chat"
    
    def detect_template_type(self, uploaded_preview: Dict[str, List[str]]) -> Tuple[TemplateType, float]:
        """
        Detect which template type the uploaded data belongs to
        Returns: (template_type, confidence_score)
        """
        # First try rule-based detection for performance
        rule_based_result = self._rule_based_detection(uploaded_preview)
        if rule_based_result[1] > 0.8:  # High confidence threshold
            return rule_based_result
        
        # Fall back to LLM-based detection for ambiguous cases
        return self._llm_based_detection(uploaded_preview)
    
    def _rule_based_detection(self, uploaded_preview: Dict[str, List[str]]) -> Tuple[TemplateType, float]:
        """Rule-based template detection using key indicators"""
        column_names = [col.lower().strip() for col in uploaded_preview.keys()]
        template_scores = {}
        
        for template_type, config in self.template_manager.get_all_templates().items():
            score = 0
            total_indicators = len(config.key_indicators)
            
            for indicator in config.key_indicators:
                indicator_lower = indicator.lower()
                # Check for exact matches or partial matches
                for col_name in column_names:
                    if indicator_lower in col_name or col_name in indicator_lower:
                        score += 1
                        break
            
            # Normalize score
            confidence = score / total_indicators if total_indicators > 0 else 0
            template_scores[template_type] = confidence
        
        # Get the template with highest score
        best_template = max(template_scores.items(), key=lambda x: x[1])
        return best_template
    
    def _llm_based_detection(self, uploaded_preview: Dict[str, List[str]]) -> Tuple[TemplateType, float]:
        """LLM-based template detection for ambiguous cases"""
        try:
            templates_info = {}
            for template_type, config in self.template_manager.get_all_templates().items():
                templates_info[template_type.value] = {
                    "name": config.name,
                    "description": config.description,
                    "key_indicators": config.key_indicators,
                    "required_columns": config.required_columns
                }
            
            system_prompt = self._build_detection_system_prompt(templates_info)
            user_prompt = f"""
            Analyze the following uploaded data and determine which template type it belongs to:
            
            Column names and sample values:
            {json.dumps(uploaded_preview, indent=2)}
            
            Consider:
            1. The column names and their semantic meaning
            2. The sample data values
            3. The overall structure and context
            
            Respond with JSON in this format:
            {{
                "template_type": "customer|product",
                "confidence": 0.95,
                "reasoning": "Brief explanation of why this template was chosen"
            }}
            """
            
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                stream=False,
            )
            
            content = response.choices[0].message.content
            cleaned = clean_json_response(content)
            result = json.loads(cleaned)
            
            template_type_str = result.get("template_type", "").lower()
            confidence = float(result.get("confidence", 0.0))
            
            # Map string to enum
            template_type_map = {
                "customer": TemplateType.CUSTOMER,
                "product": TemplateType.PRODUCT,
                "audit_trail": TemplateType.AUDIT_TRAIL,
                "supplier": TemplateType.SUPPLIER
            }
            
            if template_type_str not in template_type_map:
                raise ValueError(f"Unknown template type: {template_type_str}")
            
            return template_type_map[template_type_str], confidence
            
        except Exception as e:
            print(f"Error in LLM-based template detection: {str(e)}")
            # Fallback to customer template as default
            return TemplateType.CUSTOMER, 0.5
    
    def _build_detection_system_prompt(self, templates_info: Dict) -> str:
        """Build system prompt for template detection"""
        return f"""
        You are a template detection agent that analyzes uploaded data to determine which Sage 50 template type it belongs to.
        
        Available template types:
        {json.dumps(templates_info, indent=2)}
        
        Your job is to:
        1. Analyze the column names and sample values
        2. Match them against the key indicators for each template type
        3. Determine the most likely template type
        4. Provide a confidence score (0.0 to 1.0)
        
        Guidelines:
        - Customer templates typically contain: names, addresses, contact info, financial terms, account references
        - Product templates typically contain: stock codes, descriptions, prices, categories, suppliers, inventory info
        - Audit Trail templates typically contain: transaction types, amounts, dates, references, tax codes, nominal accounts
        - Supplier templates typically contain: supplier codes, vendor names, contact info, payment terms, purchase-related fields
        - Look for semantic patterns, not just literal matches
        - Consider the overall context and data structure
        
        Respond only with valid JSON in the specified format.
        """
