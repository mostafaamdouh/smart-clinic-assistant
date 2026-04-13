"""
RAG Pipeline for Smart Clinic Assistant
Person 2 — RAG System
"""

import chromadb
from chromadb.utils import embedding_functions

from data import DOCTORS, PATIENT_HISTORIES, MEDICAL_ARTICLES

# ─── Constants ────────────────────────────────────────────────────────────────

CHROMA_PATH = "./chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

COLLECTION_DOCTORS  = "doctors"
COLLECTION_PATIENTS = "patients"
COLLECTION_ARTICLES = "articles"

# ─── Embedding Function ───────────────────────────────────────────────────────

def get_embedding_fn():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

# ─── ChromaDB Client ──────────────────────────────────────────────────────────

def get_chroma_client():
    return chromadb.PersistentClient(path=CHROMA_PATH)

# ─── Document Preparation ─────────────────────────────────────────────────────

def prepare_doctor_docs():
    docs, ids, metas = [], [], []
    for doc in DOCTORS:
        text = (
            f"Doctor: {doc['name']}\n"
            f"Specialization: {doc['specialization']}\n"
            f"Bio: {doc['bio']}\n"
            f"Conditions treated: {', '.join(doc['conditions_treated'])}\n"
            f"Schedule: {doc['schedule']}"
        )
        docs.append(text)
        ids.append(doc["id"])
        metas.append({
            "name": doc["name"],
            "specialization": doc["specialization"],
            "type": "doctor_profile",
        })
    return docs, ids, metas


def prepare_patient_docs():
    docs, ids, metas = [], [], []
    for patient in PATIENT_HISTORIES:
        for i, visit in enumerate(patient["visits"]):
            text = (
                f"Patient: {patient['name']} (ID: {patient['patient_id']}), "
                f"Age: {patient['age']}, Gender: {patient['gender']}\n"
                f"Visit Date: {visit['date']}\n"
                f"Doctor: {visit['doctor']} ({visit['specialization']})\n"
                f"Complaint: {visit['complaint']}\n"
                f"Diagnosis: {visit['diagnosis']}\n"
                f"Prescription: {visit['prescription']}\n"
                f"Notes: {visit['notes']}\n"
                f"Follow-up: {visit['follow_up']}"
            )
            doc_id = f"{patient['patient_id']}_visit_{i+1}"
            docs.append(text)
            ids.append(doc_id)
            metas.append({
                "patient_id": patient["patient_id"],
                "patient_name": patient["name"],
                "visit_date": visit["date"],
                "doctor": visit["doctor"],
                "type": "patient_history",
            })
    return docs, ids, metas


def prepare_article_docs():
    docs, ids, metas = [], [], []
    for article in MEDICAL_ARTICLES:
        text = (
            f"Title: {article['title']}\n"
            f"Specialization: {article['specialization']}\n"
            f"Content: {article['content']}\n"
            f"Keywords: {', '.join(article['keywords'])}"
        )
        docs.append(text)
        ids.append(article["id"])
        metas.append({
            "title": article["title"],
            "specialization": article["specialization"],
            "type": "medical_article",
        })
    return docs, ids, metas

# ─── Indexing ─────────────────────────────────────────────────────────────────

def index_all():
    client   = get_chroma_client()
    embed_fn = get_embedding_fn()

    print("📚 Indexing knowledge base into ChromaDB...\n")

    for name, prep_fn in [
        (COLLECTION_DOCTORS,  prepare_doctor_docs),
        (COLLECTION_PATIENTS, prepare_patient_docs),
        (COLLECTION_ARTICLES, prepare_article_docs),
    ]:
        try:
            client.delete_collection(name)
        except Exception:
            pass

        collection = client.create_collection(
            name=name,
            embedding_function=embed_fn,
        )

        docs, ids, metas = prep_fn()
        collection.add(documents=docs, ids=ids, metadatas=metas)
        print(f"  ✅ '{name}' collection — {len(docs)} documents indexed.")

    print("\n🎉 All documents indexed successfully!")

# ─── Retrieval ────────────────────────────────────────────────────────────────

class RAGRetriever:
    def __init__(self):
        self.client   = get_chroma_client()
        self.embed_fn = get_embedding_fn()
        self.collections = {
            name: self.client.get_collection(name, embedding_function=self.embed_fn)
            for name in [COLLECTION_DOCTORS, COLLECTION_PATIENTS, COLLECTION_ARTICLES]
        }

    def retrieve(self, query: str, n_results: int = 3) -> list:
        results = []
        for col_name, collection in self.collections.items():
            try:
                res = collection.query(
                    query_texts=[query],
                    n_results=n_results,
                )
                for text, meta, dist in zip(
                    res["documents"][0],
                    res["metadatas"][0],
                    res["distances"][0],
                ):
                    results.append({
                        "source":   col_name,
                        "text":     text,
                        "metadata": meta,
                        "distance": dist,
                    })
            except Exception as e:
                print(f"  ⚠️  Error querying '{col_name}': {e}")

        results.sort(key=lambda x: x["distance"])
        return results

    def retrieve_formatted(self, query: str, n_results: int = 3) -> str:
        results = self.retrieve(query, n_results)
        if not results:
            return "No relevant information found in the knowledge base."

        context_parts = []
        for i, r in enumerate(results, 1):
            context_parts.append(
                f"[Source {i} — {r['source']}]\n{r['text']}"
            )
        return "\n\n---\n\n".join(context_parts)

# ─── Quick Test ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    index_all()

    print("\n" + "=" * 60)
    print("🔍 Testing retrieval...\n")

    retriever = RAGRetriever()

    test_queries = [
        "What did the doctor prescribe for Mohamed Ali last visit?",
        "Who is the dermatology doctor and when is he available?",
        "What is the treatment for psoriasis?",
    ]

    for q in test_queries:
        print(f"❓ Query: {q}")
        result = retriever.retrieve_formatted(q, n_results=2)
        print(result)
        print("\n" + "=" * 60 + "\n")