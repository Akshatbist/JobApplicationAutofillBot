from sentence_transformers import SentenceTransformer
import chromadb

class AnswerDatabase():
    
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.Client()

        self.collection_names = [collection.name for collection in self.chroma_client.list_collections()]

        if "qa-memory" in self.collection_names:
            self.collection = self.chroma_client.get_collection(name="qa-memory")
        else:
            self.collection = self.chroma_client.create_collection(name="qa-memory")

    def store_qa(self, question, context):
        embedding = self.model.encode(question).tolist()
        safe_id = question[:20].replace(" ", "_").replace("?", "").replace("/", "_")
        self.collection.add(
                documents=[question],
                embeddings=[embedding],
                metadatas=[{"answer": context}],
                ids=[safe_id]  # Safe ID
            )
    def query_similar(self, question, top_k=1):
        embedding = self.model.encode(question).tolist()
        results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k
            )
        return results['documents'], results['metadatas']




    