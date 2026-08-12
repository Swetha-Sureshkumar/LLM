from io import BytesIO
from typing import List, Dict, Any

from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uuid


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or '')
        except Exception:
            texts.append('')
    return '\n'.join(texts)


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
    if not text:
        return []
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = min(start + chunk_size, length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
        if start >= length:
            break
    return chunks


class RAGStore:
    """In-memory RAG store using TF-IDF + cosine similarity."""

    def __init__(self):
        self._docs: Dict[str, Dict[str, Any]] = {}

    def add_pdf(self, pdf_bytes: bytes, doc_id: str = None, filename: str = None) -> str:
        text = extract_text_from_pdf_bytes(pdf_bytes)
        return self.add_text(text, doc_id=doc_id, filename=filename)

    def add_text(self, text: str, doc_id: str = None, filename: str = None) -> str:
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        chunks = chunk_text(text)
        if not chunks:
            self._docs[doc_id] = {'chunks': [], 'vectorizer': None, 'matrix': None, 'meta': {'filename': filename}}
            return doc_id

        vectorizer = TfidfVectorizer().fit(chunks)
        matrix = vectorizer.transform(chunks)

        self._docs[doc_id] = {
            'chunks': chunks,
            'vectorizer': vectorizer,
            'matrix': matrix,
            'meta': {'filename': filename},
        }
        return doc_id

    def query(self, doc_id: str, question: str, top_k: int = 3):
        doc = self._docs.get(doc_id)
        if not doc or not doc.get('matrix'):
            return []

        vec = doc['vectorizer'].transform([question])
        sims = cosine_similarity(vec, doc['matrix'])[0]
        ranked_idx = sims.argsort()[::-1][:top_k]
        results = []
        for idx in ranked_idx:
            results.append({'chunk': doc['chunks'][idx], 'score': float(sims[idx]), 'index': int(idx)})
        return results


rag_store = RAGStore()
