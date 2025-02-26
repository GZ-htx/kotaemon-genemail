import logging
from typing import Generator

from htx.pipelines.answer_long_context import AnswerWithLongContext
from htx.reasoning.genscheda import GenSchedaPipeline
from kotaemon.base import Document, RetrievedDocument
from kotaemon.indices.qa.citation_qa import DEFAULT_QA_TEXT_PROMPT
from ktem.llms.manager import llms
from ktem.utils import SUPPORTED_LANGUAGE_MAP

logger = logging.getLogger(__name__)


class GenSchedaPipelineLC(GenSchedaPipeline):

    def retrieve(
        self, message: str, history: list
    ) -> list[RetrievedDocument]:

        query = None
        if not query:
            # TODO: previously return [], [] because we think this message as something
            # like "Hello", "I need help"...
            query = message

        docs, doc_ids = [], []

        for idx, retriever in enumerate(self.retrievers):
            retriever_node = self._prepare_child(retriever, f"retriever_{idx}")
            retriever_docs = retriever_node(text=query)

            retriever_docs_text = []
            retriever_docs_plot = []

            for doc in retriever_docs:
                if doc.metadata.get("type", "") == "plot":
                    retriever_docs_plot.append(doc)
                else:
                    retriever_docs_text.append(doc)

            for doc in retriever_docs_text:
                if doc.doc_id not in doc_ids:
                    docs.append(doc)

        return docs

    def stream(  # type: ignore
        self, message: str, conv_id: str, history: list, **kwargs  # type: ignore
    ) -> Generator[Document, None, Document]:
        # should populate the context
        docs = self.retrieve(message, history)
        print(f"Got {len(docs)} retrieved documents")

        evidence_mode, evidence, images = self.evidence_pipeline(docs).content

        answer = yield from self.answering_pipeline.stream(
            question=message,
            history=history,
            evidence=evidence,
            evidence_mode=evidence_mode,
            images=images,
            conv_id=conv_id,
            **kwargs,
        )

        return answer

    @classmethod
    def get_info(cls) -> dict:
        return {
            "id": "scheda-gen-entire-document",
            "name": "Scheda Generation with long context",
            "description": (
                "Pipeline for the generation of schede using the entire document"
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
                "value": 1,
                "component": "number",
                "info": "The maximum number of chat interactions to include in the LLM",
            }
        }

    @classmethod
    def get_pipeline(cls, settings, states, retrievers):
        """Get the reasoning pipeline

        Args:
            settings: the settings for the pipeline
            retrievers: the retrievers to use
        """
        pipeline = cls.prepare_pipeline_instance(settings, retrievers)

        prefix = f"reasoning.options.{cls.get_info()['id']}"
        llm_name = settings.get(f"{prefix}.llm", None)
        llm = llms.get(llm_name, llms.get_default())

        # prepare evidence pipeline configuration
        evidence_pipeline = pipeline.evidence_pipeline
        evidence_pipeline.max_context_length = 128000

        # answering pipeline configuration
        answer_pipeline = pipeline.answering_pipeline = AnswerWithLongContext()

        answer_pipeline.llm = llm
        answer_pipeline.n_last_interactions = settings[f"{prefix}.n_last_interactions"]
        answer_pipeline.system_prompt = settings[f"{prefix}.system_prompt"]
        answer_pipeline.qa_template = settings[f"{prefix}.qa_prompt"]
        answer_pipeline.lang = SUPPORTED_LANGUAGE_MAP.get(
            settings["reasoning.lang"], "English"
        )

        return pipeline
