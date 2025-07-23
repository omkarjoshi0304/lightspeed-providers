# from typing import Any, List, Dict
# from pydantic import BaseModel, Field
# import yaml
# import os

# class RedactionShieldConfig(BaseModel):
#     """Configuration for redaction shield."""
    
#     config_file: str = Field(
#         default="config/redaction_config.yaml",
#         description="Path to YAML configuration file with redaction patterns",
#     )
    
#     log_redactions: bool = Field(
#         default=True,
#         description="Whether to log when redactions are applied",
#     )
    
#     @classmethod
#     def sample_run_config(
#         cls,
#         config_file: str = "config/redaction_config.yaml",
#         log_redactions: bool = True,
#         **kwargs,
#     ) -> dict[str, Any]:
#         return {
#             "config_file": config_file,
#             "log_redactions": log_redactions,
#         }
    
#     def load_patterns(self) -> List[Dict[str, str]]:
#         """Load redaction patterns from YAML file."""
#         try:
#             if not os.path.exists(self.config_file):
#                 return []
            
#             with open(self.config_file, 'r') as f:
#                 config = yaml.safe_load(f)
            
#             return config.get("redaction_patterns", [])
            
#         except Exception:
#             return []

import os
import yaml
from typing import Any, List, Dict

class RedactionShieldConfig:
    """Configuration for redaction shield."""
    
    def __init__(self, config_file: str = "config/redaction_config.yaml", log_redactions: bool = True):
        self.config_file = config_file
        self.log_redactions = log_redactions
    
    @classmethod
    def sample_run_config(
        cls,
        config_file: str = "config/redaction_config.yaml",
        log_redactions: bool = True,
        **kwargs,
    ) -> dict[str, Any]:
        return {
            "config_file": config_file,
            "log_redactions": log_redactions,
        }
    
    def load_patterns(self) -> List[Dict[str, str]]:
        """Load redaction patterns from YAML file."""
        try:
            if not os.path.exists(self.config_file):
                print(f"Config file {self.config_file} not found")
                return []
            
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            return config.get("redaction_patterns", [])
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return []