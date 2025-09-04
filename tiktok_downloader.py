import os
import re
import requests
from urllib.parse import urlparse
import yt_dlp

class TikTokDownloader:
    """Classe pour télécharger des vidéos TikTok et extraire l'audio"""
    
    def __init__(self):
        """Initialisation du téléchargeur TikTok"""
        self.download_folder = 'downloads'
        os.makedirs(self.download_folder, exist_ok=True)
        
        # Configuration yt-dlp pour TikTok
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
        }
        
        # Options pour l'extraction audio uniquement
        self.audio_opts = self.ydl_opts.copy()
        self.audio_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
        
        # Options pour le téléchargement vidéo complet
        self.video_opts = self.ydl_opts.copy()
        self.video_opts.update({
            'format': 'best[ext=mp4]/best',
        })
    
    def validate_tiktok_url(self, url):
        """Valide qu'une URL est bien une URL TikTok"""
        tiktok_patterns = [
            r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'https?://(?:vm|vt)\.tiktok\.com/[\w]+',
            r'https?://(?:www\.)?tiktok\.com/t/[\w]+',
        ]
        
        return any(re.match(pattern, url) for pattern in tiktok_patterns)
    
    def download_video(self, url):
        """
        Télécharge une vidéo TikTok et extrait l'audio en MP3
        
        Args:
            url (str): URL de la vidéo TikTok
            
        Returns:
            str: Chemin vers le fichier audio extrait
        """
        if not self.validate_tiktok_url(url):
            raise ValueError("URL TikTok invalide")
        
        try:
            with yt_dlp.YoutubeDL(self.audio_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Récupérer le nom du fichier généré
                filename = ydl.prepare_filename(info)
                # Remplacer l'extension par .mp3
                audio_filename = os.path.splitext(filename)[0] + '.mp3'
                
                if os.path.exists(audio_filename):
                    return audio_filename
                else:
                    # Si le fichier n'existe pas avec l'extension .mp3, chercher d'autres extensions
                    for ext in ['.m4a', '.webm', '.opus']:
                        alt_filename = os.path.splitext(filename)[0] + ext
                        if os.path.exists(alt_filename):
                            return alt_filename
                    
                    raise Exception("Fichier audio non trouvé après extraction")
                    
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement TikTok: {str(e)}")
    
    def download_video_only(self, url):
        """
        Télécharge uniquement la vidéo TikTok (sans extraction audio)
        
        Args:
            url (str): URL de la vidéo TikTok
            
        Returns:
            str: Chemin vers le fichier vidéo téléchargé
        """
        if not self.validate_tiktok_url(url):
            raise ValueError("URL TikTok invalide")
        
        try:
            with yt_dlp.YoutubeDL(self.video_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                # Récupérer le nom du fichier généré
                filename = ydl.prepare_filename(info)
                
                # Chercher le fichier avec différentes extensions possibles
                for ext in ['.mp4', '.webm', '.mkv']:
                    video_filename = os.path.splitext(filename)[0] + ext
                    if os.path.exists(video_filename):
                        return video_filename
                
                # Si aucun fichier n'est trouvé, utiliser le nom par défaut
                if os.path.exists(filename):
                    return filename
                    
                raise Exception("Fichier vidéo non trouvé après téléchargement")
                    
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement de la vidéo TikTok: {str(e)}")
    
    def get_video_info(self, url):
        """
        Récupère les informations d'une vidéo TikTok sans la télécharger
        
        Args:
            url (str): URL de la vidéo TikTok
            
        Returns:
            dict: Informations sur la vidéo
        """
        if not self.validate_tiktok_url(url):
            raise ValueError("URL TikTok invalide")
        
        try:
            opts = self.ydl_opts.copy()
            opts['skip_download'] = True
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'title': info.get('title', 'Sans titre'),
                    'author': info.get('uploader', 'Inconnu'),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'description': info.get('description', ''),
                    'upload_date': info.get('upload_date', ''),
                }
                
        except Exception as e:
            raise Exception(f"Erreur lors de la récupération des infos TikTok: {str(e)}")


# Test de la classe
if __name__ == "__main__":
    downloader = TikTokDownloader()
    
    # Test de validation d'URL
    test_urls = [
        "https://www.tiktok.com/@username/video/1234567890",
        "https://vm.tiktok.com/ZMNxxxxx/",
        "https://www.instagram.com/p/test/",
        "https://www.tiktok.com/t/ZPRxxxxxxx/",
    ]
    
    print("=== Test de validation d'URL ===")
    for url in test_urls:
        is_valid = downloader.validate_tiktok_url(url)
        print(f"{url}: {'✓ Valide' if is_valid else '✗ Invalide'}")