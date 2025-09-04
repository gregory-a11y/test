import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Récupère la clé depuis les variables d'environnement (Render: envVar OPENAI_API_KEY)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    # Dossier des fichiers téléchargés (persistance configurée côté Render)
    DOWNLOAD_FOLDER = "downloads"
    ALLOWED_HOSTS = ["www.instagram.com", "instagram.com"]
    
    @staticmethod
    def init_app(app):
        pass 