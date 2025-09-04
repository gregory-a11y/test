import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Récupère la clé depuis les variables d'environnement (Render: envVar OPENAI_API_KEY)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    # Dossier des fichiers téléchargés (persistance configurée côté Render)
    DOWNLOAD_FOLDER = "downloads"
    # Optionnel: cookie de session Instagram pour contourner le login/rate limit côté serveur
    INSTAGRAM_SESSIONID = os.getenv("INSTAGRAM_SESSIONID", "")
    ALLOWED_HOSTS = ["www.instagram.com", "instagram.com"]
    
    @staticmethod
    def init_app(app):
        pass 