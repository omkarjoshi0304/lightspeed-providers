from typing import Any
from string import Template

from lightspeed_stack_providers.providers.inline.safety.lightspeed_question_validity.config import (
    QuestionValidityShieldConfig,
)

from llama_stack.apis.shields import Shield
from llama_stack.distribution.datatypes import Api
from llama_stack.providers.datatypes import ShieldsProtocolPrivate
from llama_stack.apis.safety import (
    SafetyViolation,
    ViolationLevel,
    RunShieldResponse,
    Safety,
)
from llama_stack.apis.inference import (
    Inference,
    Message,
    UserMessage,
)

SUBJECT_REJECTED = "REJECTED"
SUBJECT_ALLOWED = "ALLOWED"

# [TODO] manstis: It should be possible to _inject_ the prompt
PROMPT_TASK = """
Instructions:
- You are a question classifying tool
- You are an expert in kubernetes and openshift
- Your job is to determine where or a user's question is related to kubernetes and/or openshift technologies and to provide a one-word response.
- If a question appears to be related to kubernetes or openshift technologies, answer with the word ${allowed}, otherwise answer with the word ${rejected}.
- Do not explain your answer, just provide the one-word response. Do not give any other response.


Example Question:
Why is the sky blue?
Example Response:
${rejected}

Example Question:
Why is the grass green?
Example Response:
${rejected}

Example Question:
Why is sand yellow?
Example Response:
${rejected}

Example Question:
Can you help configure my cluster to automatically scale?
Example Response:
${allowed}

Question:
${message}
Response:
"""

# [TODO] manstis: It should be possible to _inject_ the invalid message
INVALID_MESSAGE = (
    "Hi, I'm the OpenShift Lightspeed assistant, I can help you with questions about OpenShift, "
    "please ask me a question related to OpenShift."
)

PROMPT_TEMPLATE = Template(f"{PROMPT_TASK}")


class QuestionValidityShieldImpl(Safety, ShieldsProtocolPrivate):

    def __init__(self, config: QuestionValidityShieldConfig, deps) -> None:
        self.config = config
        self.inference_api = deps[Api.inference]

    async def initialize(self) -> None:
        pass

    async def shutdown(self) -> None:
        pass

    async def register_shield(self, shield: Shield) -> None:
        pass

    async def run_shield(
        self,
        shield_id: str,
        messages: list[Message],
        params: dict[str, Any] = None,
    ) -> RunShieldResponse:
        shield = await self.shield_store.get_shield(shield_id)
        if not shield:
            raise ValueError(f"Unknown shield {shield_id}")

        messages = messages.copy()
        # [TODO] manstis: Ensure this is the latest User message
        message: UserMessage = messages[len(messages) - 1 :][0]
        model_id = self.config.model_id

        impl = QuestionValidityRunner(
            model_id=model_id,
            inference_api=self.inference_api,
        )

        return await impl.run(message)


class QuestionValidityRunner:
    def __init__(
        self,
        model_id: str,
        inference_api: Inference,
    ):
        self.model_id = model_id
        self.inference_api = inference_api

    @staticmethod
    def build_text_shield_input(message: UserMessage) -> UserMessage:
        return UserMessage(content=QuestionValidityRunner.build_prompt(message))

    @staticmethod
    def build_prompt(message: UserMessage) -> str:
        return PROMPT_TEMPLATE.substitute(
            allowed=SUBJECT_ALLOWED,
            rejected=SUBJECT_REJECTED,
            message=message.content,
        )

    @staticmethod
    def get_shield_response(response: str) -> RunShieldResponse:
        response = response.strip()
        if response == SUBJECT_ALLOWED:
            return RunShieldResponse(violation=None)

        return RunShieldResponse(
            violation=SafetyViolation(
                violation_level=ViolationLevel.ERROR,
                user_message=INVALID_MESSAGE,
            ),
        )

    async def run(self, message: UserMessage) -> RunShieldResponse:
        shield_input_message = QuestionValidityRunner.build_text_shield_input(message)

        response = await self.inference_api.chat_completion(
            model_id=self.model_id,
            messages=[shield_input_message],
            stream=False,
        )
        content = response.completion_message.content
        content = content.strip()
        return QuestionValidityRunner.get_shield_response(content)
