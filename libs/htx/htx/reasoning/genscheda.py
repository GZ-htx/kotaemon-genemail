import logging

from kotaemon.indices.qa.citation_qa import DEFAULT_QA_TEXT_PROMPT
from ktem.reasoning.simple import FullQAPipeline

logger = logging.getLogger(__name__)


class GenSchedaPipeline(FullQAPipeline):

    @classmethod
    def get_info(cls) -> dict:
        return {
            "id": "genscheda",
            "name": "Scheda Generation",
            "description": (
                "Scheda generation pipeline."
            ),
        }

    @classmethod
    def get_user_settings(cls) -> dict:
        from ktem.llms.manager import llms

        llm = ""
        choices = [("(default)", "")]
        try:
            choices += [(_, _) for _ in llms.options().keys()]
        except Exception as e:
            logger.exception(f"Failed to get LLM options: {e}")

        return {
            "llm": {
                "name": "Language model",
                "value": llm,
                "component": "dropdown",
                "choices": choices,
                "special_type": "llm",
                "info": (
                    "The language model to use for generating the answer. If None, "
                    "the application default language model will be used."
                ),
            },
            "highlight_citation": {
                "name": "Citation style",
                "value": "highlight",
                "component": "radio",
                "choices": [
                    ("highlight (verbose)", "highlight"),
                    ("inline (concise)", "inline"),
                    ("no citation", "off"),
                ],
            },
            "create_mindmap": {
                "name": "Create Mindmap",
                "value": False,
                "component": "checkbox",
            },
            "create_citation_viz": {
                "name": "Create Embeddings Visualization",
                "value": False,
                "component": "checkbox",
            },
            "use_multimodal": {
                "name": "Use Multimodal Input",
                "value": False,
                "component": "checkbox",
            },
            "system_prompt": {
                "name": "System Prompt",
                "value": "Questo è un sistema per la generazione di schede bando",
            },
            "qa_prompt": {
                "name": "QA Prompt",
                "value": DEFAULT_QA_TEXT_PROMPT,
            },
            "n_last_interactions": {
                "name": "Number of interactions to include",
                "value": 5,
                "component": "number",
                "info": "The maximum number of chat interactions to include in the LLM",
            },
            "trigger_context": {
                "name": "Maximum message length for context rewriting",
                "value": 150,
                "component": "number",
                "info": (
                    "The maximum length of the message to trigger context addition. "
                    "Exceeding this length, the message will be used as is."
                ),
            },
        }