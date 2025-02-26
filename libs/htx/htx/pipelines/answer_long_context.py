from typing import Generator

# HTX
import gradio as gr
from openai import RateLimitError

from kotaemon.base import (
    BaseComponent,
    Document,
    Node, SystemMessage, HumanMessage, AIMessage
)
from kotaemon.indices.qa.citation_qa import DEFAULT_QA_TEXT_PROMPT, DEFAULT_QA_CHATBOT_PROMPT
from kotaemon.indices.qa.format_context import EVIDENCE_MODE_TEXT

from kotaemon.llms import ChatLLM, PromptTemplate

try:
    from ktem.llms.manager import llms
except ImportError:
    raise ImportError("Please install `ktem` to use this component")


class AnswerWithLongContext(BaseComponent):

    llm: ChatLLM = Node(default_callback=lambda _: llms.get_default())
    qa_template: str = DEFAULT_QA_TEXT_PROMPT
    qa_chatbot_template: str = DEFAULT_QA_CHATBOT_PROMPT
    lang: str = "Italian"

    system_prompt: str = ""
    n_last_interactions: int = 1

    def get_prompt(self, question, evidence, evidence_mode: int):
        """Prepare the prompt and other information for LLM"""
        if evidence_mode == EVIDENCE_MODE_TEXT:
            prompt_template = PromptTemplate(self.qa_template)
        else:
            prompt_template = PromptTemplate(self.qa_chatbot_template)

        prompt = prompt_template.populate(
            context=evidence,
            question=question,
            lang=self.lang,
        )

        return prompt, evidence

    def stream(  # type: ignore
        self,
        question: str,
        evidence: str,
        evidence_mode: int = 0,
        images: list[str] = [],
        **kwargs,
    ) -> Generator[Document, None, Document]:
        history = kwargs.get("history", [])
        print(f"Got {len(images)} images")
        # check if evidence exists, use QA prompt
        if evidence:
            prompt, evidence = self.get_prompt(question, evidence, evidence_mode)
        else:
            prompt = question

        output = ""
        logprobs = []

        messages = []
        if self.system_prompt:
            messages.append(SystemMessage(content=self.system_prompt))

        for human, ai in history[-self.n_last_interactions :]:
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))

        messages.append(HumanMessage(content=prompt))

        try:
            # try streaming first
            print("Trying LLM streaming")
            for out_msg in self.llm.stream(messages):
                output += out_msg.text
                logprobs += out_msg.logprobs
                yield Document(channel="chat", content=out_msg.text)
        except NotImplementedError:
            print("Streaming is not supported, falling back to normal processing")
            output = self.llm(messages).text
            yield Document(channel="chat", content=output)
        # HTX: added exception for context too long
        except RateLimitError as e:
            if "Request too large" in str(e):
                gr.Info("Il contesto è troppo lungo!")
                output = "⚠️ Errore: Il contesto supera la lunghezza massima consentita. Utilizza il metodo senza Long Context o togli qualche allegato!"
            else:
                gr.Info("Hai superato il limite di richieste. Attendi qualche secondo e riprova.")
                output = "⚠️ Errore: Hai superato il limite di richieste al minuto. Aspetta e riprova più tardi."

            yield Document(channel="chat", content=output)

        answer = Document(
            text=output,
        )

        return answer

    def run(
        self, question: str, evidence: str, evidence_mode: int = 0, **kwargs
    ) -> Document:
        return self.invoke(question, evidence, evidence_mode, **kwargs)

    def invoke(
        self,
        question: str,
        evidence: str,
        evidence_mode: int = 0,
        images: list[str] = [],
        **kwargs,
    ) -> Document:
        raise NotImplementedError

    async def ainvoke(  # type: ignore
        self,
        question: str,
        evidence: str,
        evidence_mode: int = 0,
        images: list[str] = [],
        **kwargs,
    ) -> Document:
        raise NotImplementedError