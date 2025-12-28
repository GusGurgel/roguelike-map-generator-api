from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from os.path import join
from utils import MAIN_PATH
from typing import Literal

import dotenv
import os
import pandas as pd

dotenv.load_dotenv(join(MAIN_PATH, "..", ".env"))

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

StoreType = Literal["items", "environments", "entities"]

DATABASES = {
    "items": {
        "csv_path": join(MAIN_PATH, "tiles_data", "items_data.csv"),
        "db_path": join(MAIN_PATH, "chroma_items_db"),
        "collection_name": "Items_Descriptions"
    },
    "environments": {
        "csv_path": join(MAIN_PATH, "tiles_data", "environment_data.csv"),
        "db_path": join(MAIN_PATH, "chroma_environments_db"),
        "collection_name": "Environments_Descriptions"
    },
    "entities": {
        "csv_path": join(MAIN_PATH, "tiles_data", "entities_data.csv"),
        "db_path": join(MAIN_PATH, "chroma_entities_db"),
        "collection_name": "Entities_Descriptions"
    }
}


def get_vector_store(store_type: StoreType) -> Chroma:
    """
    Recupera o vector store baseado no tipo (items, environments, entities).
    Cria o banco se ele ainda não existir.
    """
    if store_type not in DATABASES:
        raise ValueError(f"Tipo de store inválido: {store_type}. Escolha entre: {list(DATABASES.keys())}")

    db_config = DATABASES[store_type]
    
    is_vector_database_created = os.path.exists(db_config["db_path"])

    if not is_vector_database_created:
        print(f"Criando vector store para '{store_type}'...")
        create_vector_store(store_type)

    return Chroma(
        collection_name=db_config["collection_name"],
        persist_directory=db_config["db_path"],
        embedding_function=embeddings,
    )


def create_vector_store(store_type: StoreType):
    """
    Lê o CSV específico do tipo e cria o banco vetorial correspondente.
    """
    if store_type not in DATABASES:
        raise ValueError(f"Tipo de store inválido: {store_type}")

    db_config = DATABASES[store_type]
    
    if not os.path.exists(db_config["csv_path"]):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {db_config['csv_path']}")

    df_tiles = pd.read_csv(db_config["csv_path"])
    
    documents = []
    ids = []

    for i, row in df_tiles.iterrows():
        metadata = {
            "b64image": row.get("base64", ""),
            "x": row.get("x", 0),
            "y": row.get("y", 0),
            "type": store_type # Útil para identificar a origem depois se necessário
        }

        document = Document(
            page_content=str(row["description"]),
            id=str(i),
            metadata=metadata,
        )
        ids.append(str(i))
        documents.append(document)

    vector_store = Chroma(
        collection_name=db_config["collection_name"],
        persist_directory=db_config["db_path"],
        embedding_function=embeddings,
    )

    vector_store.add_documents(documents=documents, ids=ids)
    print(f"Vector store '{store_type}' criado com sucesso em {db_config['db_path']}")


def query_vector_store(query: str, store_type: StoreType, documents_count: int = 4) -> list:
    """
    Faz uma busca no vector store especificado pelo store_type.
    """
    vector_store = get_vector_store(store_type)
    tiles = []

    retriever = vector_store.as_retriever(search_kwargs={"k": documents_count})

    relevant_docs = retriever.invoke(query)

    for document in relevant_docs:
        tile = {
            "b64image": document.metadata.get("b64image"),
            "x": int(document.metadata.get("x", 0)),
            "y": int(document.metadata.get("y", 0)),
            "description": document.page_content,
        }
        tiles.append(tile)

    return tiles