from fastapi import FastAPI
from pydantic import BaseModel
from agno.agent import Agent
from agno.db.postgres import PostgresDb
import os
from agno.models.groq import Groq
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from agno.tools.calculator import CalculatorTools

# Carrega variáveis de ambiente
load_dotenv()

# =======================
# Inicializações
# =======================

# Qdrant
api_key = os.getenv("QDRANT_API_KEY")
qdrant_url = os.getenv("QDRANT_URL")
qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=api_key if api_key else None,
)

# Modelo de embeddings
model = SentenceTransformer("/app/model")  # já baixado no Dockerfile

# Função de consulta ao Qdrant
def query_database(query: str):
    query_vector = model.encode(query).tolist()
    points = qdrant_client.query_points(
        collection_name="sb100",
        with_vectors=False,
        limit=4,
        query=query_vector,
        using="vetor_denso"
    )
    return points

# Ferramentas disponíveis
tools = [query_database, CalculatorTools()]

# Configuração do Postgres
postgres_config = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "user": os.getenv("POSTGRES_USER", "agno_user"),
    "password": os.getenv("POSTGRES_PASSWORD", "agno_password_123"),
    "database": os.getenv("POSTGRES_DB", "agno_db"),
}
postgres_url = os.getenv("POSTGRES_URL")
if postgres_url:
    db = PostgresDb(db_url=postgres_url, memory_table="my_memory_table")
else:
    db = PostgresDb(
        host=postgres_config["host"],
        port=postgres_config["port"],
        user=postgres_config["user"],
        password=postgres_config["password"],
        database=postgres_config["database"],
        memory_table="my_memory_table"
    )

# Cria o agente
agent = Agent(
    model=Groq(),
    instructions="""
    You are a helpful assistant to help farmers with soil recommendations.
    Use the knowledge_base when necessary to answer questions about soil fertilization.
    If you don't know the answer, just say you don't know. Do not try to make up an answer.
    If the answer needs to show specific data create tables for explanation.

    Keep your answers conversational and easy to understand but concise.
    """,
    tools=tools,
    db=db,
    enable_user_memories=True,
    debug_mode=True
)

# =======================
# FastAPI
# =======================
app = FastAPI(title="RAG API", version="1.0")

# Schema para requisição
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    response = agent.run(
        input=request.message,
        user_id=request.user_id,
        session_id=request.session_id
    )
    return {"response": response}
