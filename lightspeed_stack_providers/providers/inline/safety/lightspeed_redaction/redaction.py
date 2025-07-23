import logging
import re
from typing import Any, List

from lightspeed_stack_providers.providers.inline.safety.lightspeed_redaction.config import (
    RedactionShieldConfig,
)

from llama_stack.apis.shields import Shield
from llama_stack.providers.datatypes import ShieldsProtocolPrivate
from llama_stack.apis.safety import (
    RunShieldResponse,
    Safety,
)
from llama_stack.apis.inference import (
    Message,
    UserMessage,
)

log = logging.getLogger(__name__)

class RedactionShieldImpl(Safety, ShieldsProtocolPrivate):
    """Redaction shield that mutates messages directly."""
    
    def __init__(self, config: RedactionShieldConfig, deps: dict[str, Any]) -> None:
        self.config = config
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> List[dict]:
        """Load and compile redaction patterns."""
        patterns = []
        raw_patterns = self.config.load_patterns()
        
        for pattern_config in raw_patterns:
            try:
                compiled_pattern = re.compile(pattern_config["pattern"], re.IGNORECASE)
                patterns.append({
                    "pattern": compiled_pattern,
                    "replacement": pattern_config["replacement"],
                    "original": pattern_config["pattern"]
                })
                log.debug(f"Loaded pattern: {pattern_config['pattern']}")
            except re.error as e:
                log.error(f"Invalid pattern {pattern_config['pattern']}: {e}")
        
        log.info(f"Loaded {len(patterns)} redaction patterns")
        return patterns
    
    async def initialize(self) -> None:
        """Initialize the shield."""
        pass
    
    async def shutdown(self) -> None:
        """Shutdown the shield."""
        pass
    
    async def register_shield(self, shield: Shield) -> None:
        """Register a shield."""
        pass
    
    async def run_shield(
        self,
        shield_id: str,
        messages: List[Message],
        params: dict[str, Any] | None = None,
    ) -> RunShieldResponse:
        """Run the redaction shield and mutate messages directly."""
        
        # Find the last UserMessage and redact it
        for i in range(len(messages) - 1, -1, -1):
            message = messages[i]
            if isinstance(message, UserMessage):
                # Apply redaction directly to the message
                if isinstance(message.content, str):
                    original_content = message.content
                    redacted_content = self._apply_redaction(original_content)
                    
                    if redacted_content != original_content:
                        # MUTATE THE MESSAGE DIRECTLY
                        message.content = redacted_content
                        log.info(f"Redacted message content: {original_content} -> {redacted_content}")
                
                break  # Only redact the most recent UserMessage
        
        # Return no violation - redaction is not a violation
        return RunShieldResponse(violation=None)
    
    def _apply_redaction(self, content: str) -> str:
        """Apply redaction patterns to content."""
        if not content:
            return content
            
        redacted_content = content
        applied_patterns = []
        
        for pattern_info in self.patterns:
            try:
                if pattern_info["pattern"].search(redacted_content):
                    redacted_content = pattern_info["pattern"].sub(
                        pattern_info["replacement"],
                        redacted_content
                    )
                    applied_patterns.append(pattern_info["original"])
                    
                    if self.config.log_redactions:
                        log.info(f"Applied redaction pattern: {pattern_info['original']}")
                        
            except Exception as e:
                log.error(f"Error applying pattern {pattern_info['original']}: {e}")
                continue
        
        return redacted_content