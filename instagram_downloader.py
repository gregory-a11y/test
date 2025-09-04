import os
import yt_dlp
from config import Config

class InstagramDownloader:
    def __init__(self):
        self.download_folder = Config.DOWNLOAD_FOLDER
        os.makedirs(self.download_folder, exist_ok=True)
        
    def download_video(self, url):
        """
        Télécharge une vidéo Instagram et retourne le chemin du fichier audio extrait
        """
        try:
            # Configuration pour yt-dlp avec extraction audio
            # Prépare cookies/headers pour Instagram si session fournie
            cookies = None
            if getattr(Config, 'INSTAGRAM_SESSIONID', ''):
                cookies = {
                    'sessionid': Config.INSTAGRAM_SESSIONID
                }

            ydl_opts = {
                'format': 'best[ext=mp4]',  # Meilleur format MP4 disponible
                'outtmpl': f'{self.download_folder}/%(title)s.%(ext)s',
                'extractaudio': True,
                'audioformat': 'mp3',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
                },
                'cookies': cookies,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Récupère les informations de la vidéo
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'instagram_video')
                
                # Télécharge la vidéo
                ydl.download([url])
                
                # Retourne le chemin du fichier audio
                audio_path = f'{self.download_folder}/{video_title}.mp3'
                
                # Si le fichier audio n'existe pas, essaie avec le fichier vidéo
                if not os.path.exists(audio_path):
                    video_path = f'{self.download_folder}/{video_title}.mp4'
                    if os.path.exists(video_path):
                        return video_path
                    else:
                        # Cherche le premier fichier dans le dossier de téléchargement
                        files = [f for f in os.listdir(self.download_folder) if f.endswith(('.mp4', '.mp3'))]
                        if files:
                            return os.path.join(self.download_folder, files[-1])
                
                return audio_path
                
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement: {str(e)}")
    
    def download_video_only(self, url):
        """
        Télécharge une vidéo Instagram en gardant le format vidéo original
        """
        try:
            # Configuration pour yt-dlp sans extraction audio
            # Prépare cookies/headers pour Instagram si session fournie
            cookies = None
            if getattr(Config, 'INSTAGRAM_SESSIONID', ''):
                cookies = {
                    'sessionid': Config.INSTAGRAM_SESSIONID
                }

            ydl_opts = {
                'format': 'best[ext=mp4]/best',  # Meilleur format MP4 ou meilleur format disponible
                'outtmpl': f'{self.download_folder}/%(title)s.%(ext)s',
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8'
                },
                'cookies': cookies,
                # Pas d'extraction audio
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Récupère les informations de la vidéo
                info = ydl.extract_info(url, download=False)
                video_title = info.get('title', 'instagram_video')
                
                # Télécharge la vidéo
                ydl.download([url])
                
                # Retourne le chemin du fichier vidéo
                video_path = f'{self.download_folder}/{video_title}.mp4'
                
                # Si le fichier MP4 n'existe pas, cherche d'autres formats
                if not os.path.exists(video_path):
                    # Cherche tous les fichiers vidéo dans le dossier
                    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
                    files = [f for f in os.listdir(self.download_folder) 
                            if any(f.endswith(ext) for ext in video_extensions)]
                    if files:
                        # Prend le fichier le plus récent
                        latest_file = max(files, key=lambda f: os.path.getctime(os.path.join(self.download_folder, f)))
                        return os.path.join(self.download_folder, latest_file)
                
                return video_path
                
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement vidéo: {str(e)}")
    
    def validate_instagram_url(self, url):
        """
        Valide si l'URL est une URL Instagram valide
        """
        return any(host in url for host in Config.ALLOWED_HOSTS)
    
    def cleanup_downloads(self):
        """
        Nettoie les fichiers téléchargés
        """
        try:
            for filename in os.listdir(self.download_folder):
                file_path = os.path.join(self.download_folder, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
        except Exception as e:
            print(f"Erreur lors du nettoyage: {str(e)}") 