import random
from google.cloud import firestore

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
