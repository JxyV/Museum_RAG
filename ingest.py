import os
import sys
import uuid
import logging
from pathlib import Path
from typing import List

from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langchain_huggingface import HuggingFaceEmbeddings

from langchain_ollama import OllamaEmbeddings


def setup_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def getenv_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except Exception:
        return default


def load_all_documents(docs_dir: Path) -> List:
    docs = []
    if not docs_dir.exists():
        logging.warning("Docs directory does not exist: %s", docs_dir)
        return docs

    for path in docs_dir.rglob("*"):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                loader = PyPDFLoader(str(path))
                loaded = loader.load()
            elif suffix in {".txt", ".md", ".markdown"}:
                loader = TextLoader(str(path), autodetect_encoding=True)
                loaded = loader.load()
            else:
                continue

            # Attach filename into metadata
            for d in loaded:
                d.metadata = d.metadata or {}
                d.metadata["source"] = path.name

            docs.extend(loaded)
            logging.info("Loaded %d docs from %s", len(loaded), path.name)
        except Exception as e:
            logging.exception("Failed to load %s: %s", path, e)
    return docs


def build_embeddings():
    backend = os.getenv("EMBEDDING_BACKEND", "ollama").strip().lower()
    model_name = os.getenv("EMBEDDING_MODEL", "qwen3-embedding:0.6b")

    if backend == "ollama":
        # Requires local Ollama running
        base_url = os.getenv("OLLAMA_BASE_URL") or "http://localhost:11434"
        logging.info("Using OllamaEmbeddings (%s) at %s", model_name, base_url)
        return OllamaEmbeddings(model=model_name, base_url=base_url)
    else:
        # Default to HuggingFace sentence-transformers
        logging.info("Using HuggingFaceEmbeddings (%s)", model_name)
        return HuggingFaceEmbeddings(model_name=model_name)


def main() -> None:
    load_dotenv()
    setup_logging()

    docs_dir = Path(os.getenv("DOCS_DIR", "docs"))
    persist_dir = os.getenv("CHROMA_PERSIST_DIR", ".chroma")
    chunk_size = getenv_int("CHUNK_SIZE", 800)
    chunk_overlap = getenv_int("CHUNK_OVERLAP", 120)

    logging.info("Docs dir: %s | Persist dir: %s", docs_dir, persist_dir)
    raw_docs = load_all_documents(docs_dir)
    if not raw_docs:
        logging.warning("No documents loaded. Put files into %s", docs_dir)
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )
    splits = splitter.split_documents(raw_docs)

    # Add stable chunk ids for citation
    for idx, d in enumerate(splits):
        d.metadata = d.metadata or {}
        d.metadata.setdefault("source", d.metadata.get("source", "unknown"))
        d.metadata["chunk_id"] = idx  # used in citation when page missing

    embeddings = build_embeddings()

    # Create / update Chroma collection
    vectordb = Chroma(
        collection_name="rag_docs",
        embedding_function=embeddings,
        persist_directory=persist_dir,
    )

    # Clear and re-ingest for simplicity
    try:
        ids = [str(uuid.uuid4()) for _ in splits]
        vectordb.delete_collection()  # type: ignore[attr-defined]
        logging.info("Recreated Chroma collection.")
        vectordb = Chroma(
            collection_name="rag_docs",
            embedding_function=embeddings,
            persist_directory=persist_dir,
        )
    except Exception:
        # Fallback: if delete_collection not available
        logging.info("Proceeding without collection reset.")
        ids = [str(uuid.uuid4()) for _ in splits]

    vectordb.add_documents(splits, ids=ids)
    logging.info("Ingestion complete: %d chunks.", len(splits))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
