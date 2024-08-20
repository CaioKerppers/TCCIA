import random
from google.cloud import firestore
from fetch_functions import fetch_stat_multipliers
import pickle
import os

def get_random_nature(natures_ref):
    try:
        natures = natures_ref.stream()
        nature_list = [nature.id for nature in natures]
        if nature_list:
            return random.choice(nature_list)
        else:
            raise ValueError("Não há naturezas disponíveis no banco de dados.")
    except Exception as e:
        print(f"Erro ao acessar o Firestore: {e}")
        raise
    
def get_stat_multipliers():
    return fetch_stat_multipliers()

def save_model(model, filename="model.pkl"):
    """
    Save the model to a file using pickle.

    Parameters:
    model : object
        The model or object to be saved.
    filename : str
        The filename for the saved model (default is 'model.pkl').

    Returns:
    None
    """
    # Define the directory path where you want to save the model
    directory = r"models"
    
    # Ensure the directory exists
    os.makedirs(directory, exist_ok=True)
    
    # Combine the directory path and filename
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, 'wb') as file:
            pickle.dump(model, file)
        print(f"Model saved successfully at {filepath}")
    except Exception as e:
        print(f"An error occurred while saving the model: {e}")

def load_model(filename="model.pkl"):
    """
    Load a model from a file using pickle.

    Parameters:
    filename : str
        The filename of the saved model (default is 'model.pkl').

    Returns:
    model : object
        The loaded model.
    """
    # Define the directory path where the model is saved
    directory = r"models"
    
    # Combine the directory path and filename
    filepath = os.path.join(directory, filename)
    
    try:
        with open(filepath, 'rb') as file:
            model = pickle.load(file)
        print(f"Model loaded successfully from {filepath}")
        return model
    except Exception as e:
        print(f"An error occurred while loading the model: {e}")
        return None