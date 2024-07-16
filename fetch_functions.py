# fetch_functions.py
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('pokemonbattleia-firebase-adminsdk-rjtw2-9488aa62de.json')
firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_banned_pokemon():
    banned_pokemon_ref = db.collection('Bans').document('banned_pokemon')
    banned_pokemon_doc = banned_pokemon_ref.get()
    if banned_pokemon_doc.exists:
        return banned_pokemon_doc.to_dict()['banned_pokemon']
    return []

def fetch_type_chart():
    type_chart_ref = db.collection('type_chart')
    type_chart = {}
    for doc in type_chart_ref.stream():
        type_chart[doc.id] = doc.to_dict()
    return type_chart

def fetch_natures():
    natures_ref = db.collection('Natures')
    natures = {}
    for doc in natures_ref.stream():
        natures[doc.id] = doc.to_dict()
    return natures
