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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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

# Variável global para armazenar dados da última consulta
last_query_results = []

# Função de consulta ao Qdrant
def query_database(query: str) -> list:
    """
    Tool for querying the knowledge database about agricultural topics when needed

    Args: 
    query (str): Query to search in the knowledge database

    """
    global last_query_results
    
    query_vector = model.encode(query).tolist()
    points = qdrant_client.query_points(
        collection_name="sb100",
        with_vectors=False,
        limit=4,
        query=query_vector,
        using="vetor_denso"
    )
    
    # Armazena os resultados formatados para o frontend
    last_query_results = []
    for point in points.points:
        formatted_point = {
            "id": point.id,
            "score": point.score,
            "content": point.payload.get("content", ""),
            "file": point.payload.get("file", "")
        }
        last_query_results.append(formatted_point)
    
    return points.points

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
    # model=Groq(),
    # model=Groq("llama-3.1-8b-instant"),
    model=Groq("meta-llama/llama-4-scout-17b-16e-instruct"),
    instructions="""
    Você é um **Assistente Agrônomo** útil e prático. Seu objetivo é ajudar agricultores respondendo perguntas gerais sobre agricultura, utilizando a ferramenta **query_database** (base de conhecimento) sempre que necessário.

    **REGRAS CRUCIAIS (RAG e Segurança):**
    1.  **Fonte Única:** A `knowledge_base` é sua **única fonte de conhecimento**. Se a resposta não estiver lá, diga educadamente que não possui essa informação. **NUNCA invente, deduza ou tente adivinhar** dados ou respostas.
    2.  **Uso da Base:** Sempre que uma pergunta puder ser respondida com dados ou fatos agrícolas, **priorize a consulta e a citação** da `query_database`.
    3.  **Cheque Factual:** Sempre reveja se as informações fornecidas pela `query_database` fazem sentido no contexto da pergunta. Se houver inconsistências como a resposta ser para outra cultura diga que não possui essa informação.

    **ESTILO E FORMATO:**
    1.  **Tom de Voz:** Mantenha um tom de voz **conversacional, prático e confiável** (como um consultor de campo experiente).
    2.  **Fluidez:** Para manter a conversa natural e não robótica, você pode iniciar respostas com frases como:
        * "Com base nas informações que tenho..."
        * "Minha pesquisa na base de dados indica que..."
        * "Não tenho acesso a dados em tempo real, mas [a base de conhecimento] sugere que..."
    3.  **Clareza:** Suas respostas devem ser **fáceis de entender, mas concisas**. Evite jargões desnecessários ou explicações excessivamente longas.
    4.  **Dados:** Se a resposta precisar mostrar dados ou comparações específicas, utilize **tabelas claras e bem formatadas** para melhor explicação.

    **IDIOMA:**
    1.  Toda a comunicação, incluindo perguntas e respostas, deve ser **EXCLUSIVAMENTE em português do Brasil**.
    """,
    tools=tools,
    db=db,
    enable_user_memories=True,
    debug_mode=True,
    store_events=True
)

# =======================
# FastAPI
# =======================
app = FastAPI(title="RAG API", version="1.0")

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schema para requisição
class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

# Schema para resposta
class ChatResponse(BaseModel):
    response: str
    sources: list = []

@app.get("/health")
def health_check():
    """Health check endpoint para AWS ECS"""
    return {"status": "healthy", "service": "rag-api"}

@app.get("/")
def root():
    """Root endpoint"""
    return {"message": "RAG API está funcionando!", "docs": "/docs"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    global last_query_results
    
    # Limpa resultados anteriores
    last_query_results = []
    
    # Executa o agent
    response = agent.run(
        input=request.message,
        user_id=request.user_id,
        session_id=request.session_id,
    )
    
    return ChatResponse(
        response=response.content,
        sources=last_query_results
    )
