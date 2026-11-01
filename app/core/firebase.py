import os
from functools import lru_cache

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore as admin_firestore
from google.cloud import firestore

from app.core.config import settings


def _init_firebase_app() -> None:
    try:
        firebase_admin.get_app()
        return
    except ValueError:
        pass

    options = {"projectId": settings.FIREBASE_PROJECT_ID}
    if settings.FIREBASE_CREDENTIALS_PATH:
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, options)
    else:
        firebase_admin.initialize_app(options=options)


@lru_cache
def get_db() -> firestore.Client:
    """Cliente de Firestore. Se crea una sola vez, la primera vez que se usa."""
    if settings.FIRESTORE_EMULATOR_HOST:
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.FIRESTORE_EMULATOR_HOST
        return firestore.Client(project=settings.FIREBASE_PROJECT_ID)

    _init_firebase_app()
    if settings.FIREBASE_CREDENTIALS_PATH:
        return admin_firestore.client()
    return firestore.Client(project=settings.FIREBASE_PROJECT_ID)