from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from os.path import join
from utils import MAIN_PATH
# from api import Tile

import dotenv
import os
import pandas as pd

dotenv.load_dotenv(join(MAIN_PATH, "..", ".env"))

tiles_vector_db_path = join(MAIN_PATH, "./chroma_tiles_db")
tiles_filtered_csv_path = join(MAIN_PATH, "./tiles_description.csv")

embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")


def get_vector_store() -> Chroma:
    is_vector_database_created = os.path.exists(tiles_vector_db_path)

    if not is_vector_database_created:
        create_vector_store()

    return Chroma(
        collection_name="Tiles_Descriptions",
        persist_directory=tiles_vector_db_path,
        embedding_function=embeddings,
    )


def create_vector_store():
    documents = []
    ids = []
    df_tiles = pd.read_csv(tiles_filtered_csv_path)

    for i, row in df_tiles.iterrows():
        document = Document(
            page_content=row["description"],
            id=str(i),
            metadata={
                "b64image": row["base64"],
                "x": row["x"],
                "y": row["y"],
            },
        )
        ids.append(str(i))
        documents.append(document)

    vector_store = Chroma(
        collection_name="Tiles_Descriptions",
        persist_directory=tiles_vector_db_path,
        embedding_function=embeddings,
    )

    vector_store.add_documents(documents=documents, ids=ids)


def query_vector_store(query: str, documents_count: int = 4) -> list:
    vector_store = get_vector_store()
    tiles = []

    retriver = vector_store.as_retriever(search_kwargs={"k": documents_count})

    relevant_docs = retriver.invoke(query)

    for document in relevant_docs:
        tile = {
            "b64image": document.metadata["b64image"],
            "x": int(document.metadata["x"]),
            "y": int(document.metadata["y"]),
            "description": document.page_content,
        }
        tiles.append(tile)

    return tiles
