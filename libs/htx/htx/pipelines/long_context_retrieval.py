import json
import logging
import os
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from htx.components.long_context import TXT_FILES_DIR
from kotaemon.base import RetrievedDocument
from ktem.db.models import engine
from ktem.index.file.base import BaseFileIndexRetriever

logger = logging.getLogger(__name__)


class LongContextRetrievalPipeline(BaseFileIndexRetriever):
    """Class to retrieve the entire document for long context reasoning"""

    def compose_path(self, path):
        return os.path.join(TXT_FILES_DIR, path)

    def run(
        self,
        text: str,
        doc_ids: Optional[list[str]] = None,
        *args,
        **kwargs,
    ) -> list[RetrievedDocument]:
        """Retrieve document excerpts similar to the text

        Args:
            text: the text to retrieve similar documents
            doc_ids: list of document ids to constraint the retrieval
        """
        # flatten doc_ids in case of group of doc_ids are passed
        if doc_ids:
            flatten_doc_ids = []
            for doc_id in doc_ids:
                if doc_id is None:
                    raise ValueError("No document is selected")

                if doc_id.startswith("["):
                    flatten_doc_ids.extend(json.loads(doc_id))
                else:
                    flatten_doc_ids.append(doc_id)
            doc_ids = flatten_doc_ids

        print("searching in doc_ids", doc_ids)
        if not doc_ids:
            logger.info(f"Skip retrieval because of no selected files: {self}")
            return []

        with Session(engine) as session:
            stmt = select(self.Source.path).where(self.Source.id.in_(doc_ids))
            results = session.execute(stmt)
            paths = [r[0] for r in results.all()]

        print(paths)

        docs = []

        for path in paths:
            with open(self.compose_path(path), "r") as f:
                text = f.read()
                docs.append(RetrievedDocument(doc_id=path, text=text))

        return docs

    @classmethod
    def get_pipeline(cls, user_settings, index_settings, selected):
        """Get retriever objects associated with the index

        Args:
            settings: the settings of the app
            kwargs: other arguments
        """
        retriever = cls()
        kwargs = {".doc_ids": selected}
        retriever.set_run(kwargs, temp=False)
        return retriever