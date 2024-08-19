import random
from google.cloud import firestore
from fetch_functions import fetch_stat_multipliers

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

def save_model(model_name, model_data):
    db = firestore.Client()
    try:
        doc_ref = db.collection('models').document(model_name)
        doc_ref.set(model_data)
        print(f"Modelo {model_name} salvo com sucesso.")
    except Exception as e:
        print(f"Erro ao salvar o modelo {model_name}: {e}")
        raise
