from os.path import join, dirname, realpath
from pydantic import BaseModel
import pickle
from typing import TypeVar, Type


MAIN_PATH = realpath(join(dirname("__file__"), "."))

T = TypeVar("T")


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
