from os.path import join, dirname, realpath
from pydantic import BaseModel
import pickle
from typing import TypeVar, Type


MAIN_PATH = realpath(join(dirname("__file__"), "."))

# Definindo um TypeVar para garantir que o retorno seja do mesmo tipo do modelo passado
T = TypeVar("T", bound=BaseModel)


def save_object_json(obj: BaseModel, file_path: str) -> None:
    """
    Salva um objeto Pydantic em um arquivo JSON.
    Utiliza o método model_dump_json() do Pydantic V2.
    """
    try:
        # Pydantic V2 usa model_dump_json().
        # Se estiver usando V1, seria obj.json()
        json_str = obj.model_dump_json(indent=2)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(json_str)
        print(f"Successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving object to JSON: {e}")


def load_object_json(file_path: str, model_type: Type[T]) -> T:
    """
    Carrega um arquivo JSON e o converte para uma instância do modelo Pydantic especificado.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            json_content = file.read()

        # Pydantic V2 usa model_validate_json().
        # Se estiver usando V1, seria model_type.parse_raw()
        obj = model_type.model_validate_json(json_content)

        print(f"Successfully loaded from {file_path}")
        return obj
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        raise
    except Exception as e:
        print(f"Error loading object from JSON: {e}")
        raise


def save_object(obj, file_path: str) -> None:
    """
    Saves a Python object (like your Pydantic models) to a file using pickle.
    """
    try:
        with open(file_path, "wb") as file:
            pickle.dump(obj, file)
        print(f"Successfully saved to {file_path}")
    except Exception as e:
        print(f"Error saving object: {e}")


def load_object(file_path: str, model_type: Type[T]) -> T:
    """
    Loads a pickled object from a file.
    'model_type' is used for type hinting and clarity.
    """
    try:
        with open(file_path, "rb") as file:
            obj = pickle.load(file)
        print(f"Successfully loaded from {file_path}")
        return obj
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        raise
    except Exception as e:
        print(f"Error loading object: {e}")
        raise
