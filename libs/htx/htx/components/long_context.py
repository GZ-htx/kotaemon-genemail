import os
from pathlib import Path, PosixPath
from llama_index.readers.file import PDFReader

from theflow.settings import settings as flowsettings
KH_APP_DATA_DIR = getattr(flowsettings, "KH_APP_DATA_DIR", ".")
TXT_FILES_DIR = os.path.join(KH_APP_DATA_DIR, "user_data", "txt_files")


def get_text_from_filepath(path: str):
    pdf_reader = PDFReader()
    file_path = Path(path)
    docs = pdf_reader.load_data(file_path)

    full_text = "\n".join([doc.text for doc in docs])
    return full_text


def store_txt_file(file_path: str | Path, file_name: str):
    """
    Store a text file in the user_data/txt_files directory.
    """
    print("Adding txt file")
    full_text = get_text_from_filepath(file_path)
    with open(os.path.join(TXT_FILES_DIR, file_name), "w") as f:
        f.write(full_text)
