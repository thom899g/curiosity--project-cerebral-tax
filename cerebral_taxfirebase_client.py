"""
Firebase client for state management and event persistence.
Uses Firestore for document storage with robust error handling.
"""
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1 import Client as FirestoreClient
    from google.cloud.firestore_v1.document import DocumentReference
    from google.cloud.firestore_v1.collection import CollectionReference
    from google.cloud.exceptions import GoogleCloudError
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False