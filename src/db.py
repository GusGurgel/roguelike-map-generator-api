import sqlite3
from datetime import datetime
from typing import List, Optional, Any, Dict
from pathlib import Path
from models import AssetBundle
from os.path import join
from utils import MAIN_PATH

# Define o caminho do banco de dados na raiz do projeto (um nível acima de src/)
DB_PATH = join(MAIN_PATH, "database.db")


def get_db_connection() -> sqlite3.Connection:
    """Cria e retorna uma conexão com o banco de dados configurada para retornar Rows."""
    conn = sqlite3.connect(DB_PATH)
    # Permite acessar colunas pelo nome (ex: row['name'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa o banco de dados criando a tabela se não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assets_bundles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            llm_model TEXT,
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            bundle_data TEXT NOT NULL
        )
    """
    )

    conn.commit()
    conn.close()


# Garante que a tabela existe ao importar este módulo (opcional, mas útil)
init_db()


def insert_asset_bundle(
    name: str, description: str, llm_model: str, bundle_data: AssetBundle
) -> int:
    """
    Insere um novo asset bundle e retorna o id dessa inserção.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Serializa o modelo Pydantic para JSON string
    # Nota: Em Pydantic v2 usa-se model_dump_json(), na v1 usa-se .json()
    json_data = bundle_data.model_dump_json()
    created_at = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO assets_bundles (name, description, llm_model, create_at, bundle_data)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, description, llm_model, created_at, json_data),
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return new_id if new_id != None else -1


def find_all_assets_bundles() -> List[Dict[str, Any]]:
    """
    Retorna todos os asset bundles como uma lista de dicionários.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, llm_model, create_at FROM assets_bundles ORDER BY create_at DESC"
    )
    rows = cursor.fetchall()

    # Converte sqlite3.Row para dict para facilitar o uso na API
    result = [dict(row) for row in rows]

    conn.close()
    return result


def find_bundle_data_by_id(id: int) -> Optional[AssetBundle]:
    """
    Retorna o bundle_data de um asset bundle usando o id, já convertido para o objeto Pydantic.
    Retorna None se não encontrar.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT bundle_data FROM assets_bundles WHERE id = ?", (id,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    json_str = row["bundle_data"]

    try:
        # Reconstrói o objeto Pydantic a partir da string JSON
        return AssetBundle.model_validate_json(json_str)
    except Exception as e:
        print(f"Erro ao deserializar bundle_data para id {id}: {e}")
        return None


def delete_asset_bundle_by_id(id: int) -> bool:
    """
    Deleta um asset bundle pelo id e retorna True se ele foi deletado, False caso contrário.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM assets_bundles WHERE id = ?", (id,))
    conn.commit()

    rows_deleted = cursor.rowcount
    conn.close()

    return rows_deleted > 0
