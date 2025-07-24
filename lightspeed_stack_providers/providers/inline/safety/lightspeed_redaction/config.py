from typing import Any, List
from pydantic import BaseModel, Field

class PatternReplacement(BaseModel):
    """A single redaction pattern and its replacement."""
    pattern: str = Field(description="Regular expression pattern to match")
    replacement: str = Field(description="Text to replace matches with")

class RedactionShieldConfig(BaseModel):
    """Configuration for redaction shield with inline rules."""
    
    rules: List[PatternReplacement] = Field(
        default=[],
        description="List of redaction rules with pattern and replacement",
    )
    
    case_sensitive: bool = Field(
        default=False,
        description="Whether pattern matching is case sensitive",
    )
    
    @classmethod
    def sample_run_config(
        cls,
        rules: List[dict] | None = None,
        log_redactions: bool = True,
        case_sensitive: bool = False,
        **kwargs,
    ) -> dict[str, Any]:
        return {
            "rules": rules,
            "log_redactions": log_redactions,
            "case_sensitive": case_sensitive,
        }