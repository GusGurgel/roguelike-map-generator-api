import sqlite3
from datetime import datetime
from typing import List, Optional, Any, Dict
from pathlib import Path
from models import AssetBundle
from os.path import join
from utils import MAIN_PATH

DB_PATH = join(MAIN_PATH, "database.db")


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa o banco de dados criando a tabela se não existir."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Adicionada a coluna generation_time (REAL para aceitar decimais)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS assets_bundles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            llm_model TEXT,
            generation_time REAL, 
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            bundle_data TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


# Inicializa o DB
init_db()

# Se você já tem um banco criado anteriormente, descomente a linha abaixo e rode uma vez:
# migrate_add_generation_time_column()


def insert_asset_bundle(
    asset_bundle: AssetBundle,
    llm_model: str,
) -> int:
    """
    Insere um novo asset bundle.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    json_data = asset_bundle.model_dump_json()
    created_at = datetime.now().isoformat()

    # Atualizado o SQL para incluir generation_time
    cursor.execute(
        """
        INSERT INTO assets_bundles (name, description, llm_model, generation_time, create_at, bundle_data)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            asset_bundle.name,
            asset_bundle.description,
            llm_model,
            asset_bundle.generation_time_seconds,
            created_at,
            json_data,
        ),
    )

    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return new_id if new_id is not None else -1


def find_all_assets_bundles() -> List[Dict[str, Any]]:
    """
    Retorna todos os asset bundles.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Adicionado generation_time no SELECT
    cursor.execute(
        "SELECT id, name, llm_model, generation_time, create_at FROM assets_bundles ORDER BY create_at DESC"
    )
    rows = cursor.fetchall()

    result = [dict(row) for row in rows]

    conn.close()
    return result


def find_bundle_data_by_id(id: int) -> Optional[AssetBundle]:
    """Retorna o bundle_data de um asset bundle."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT bundle_data FROM assets_bundles WHERE id = ?", (id,))
    row = cursor.fetchone()

    conn.close()

    if row is None:
        return None

    json_str = row["bundle_data"]

    try:
        return AssetBundle.model_validate_json(json_str)
    except Exception as e:
        print(f"Erro ao deserializar bundle_data para id {id}: {e}")
        return None


def delete_asset_bundle_by_id(id: int) -> bool:
    """Deleta um asset bundle pelo id."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM assets_bundles WHERE id = ?", (id,))
    conn.commit()

    rows_deleted = cursor.rowcount
    conn.close()

    return rows_deleted > 0
