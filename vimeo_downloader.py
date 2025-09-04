import os
import re
import requests
import yt_dlp
from config import Config


class VimeoDownloader:
    """Téléchargeur pour vidéos Vimeo (audio et vidéo)."""

    def __init__(self):
        self.download_folder = Config.DOWNLOAD_FOLDER
        os.makedirs(self.download_folder, exist_ok=True)

        # Options communes yt-dlp
        self.base_opts = {
            'quiet': True,
            'no_warnings': True,
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'retries': 3,
            'fragment_retries': 3,
            'extractor_retries': 3,
            'noplaylist': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Origin': 'https://vimeo.com',
                'Referer': 'https://vimeo.com',
            }
        }

        # Extraction audio (MP3)
        self.audio_opts = self.base_opts.copy()
        self.audio_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })

        # Téléchargement vidéo (MP4 si possible)
        self.video_opts = self.base_opts.copy()
        self.video_opts.update({
            'format': 'best[ext=mp4]/best'
        })

    def validate_vimeo_url(self, url: str) -> bool:
        """Valide si l'URL correspond à un format Vimeo connu."""
        patterns = [
            r'https?://(?:www\.)?vimeo\.com/\d+',
            r'https?://(?:www\.)?vimeo\.com/channels/[\w-]+/\d+',
            r'https?://player\.vimeo\.com/video/\d+',
            r'https?://(?:www\.)?vimeo\.com/ondemand/[\w-]+/\d+',
        ]
        return any(re.match(p, url) for p in patterns)

    def _extract_video_id(self, url: str) -> str:
        match = re.search(r'(?:vimeo\.com/(?:.*?/)?(\d+)|player\.vimeo\.com/video/(\d+))', url)
        if not match:
            return ''
        return match.group(1) or match.group(2)

    def _fetch_player_config(self, video_id: str) -> dict:
        """Récupère le JSON de configuration du player Vimeo pour obtenir des URLs directes."""
        endpoints = [
            f'https://player.vimeo.com/video/{video_id}/config',
            f'https://player.vimeo.com/video/{video_id}/config?autoplay=1&dnt=1',
        ]
        headers = {
            'User-Agent': self.base_opts['http_headers']['User-Agent'],
            'Referer': f'https://vimeo.com/{video_id}',
            'Origin': 'https://vimeo.com',
            'Accept': 'application/json,text/html;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        for endpoint in endpoints:
            try:
                resp = requests.get(endpoint, headers=headers, timeout=10)
                if resp.status_code == 200 and resp.headers.get('content-type', '').startswith('application/json'):
                    return resp.json()
            except Exception:
                continue
        return {}

    def _get_best_direct_url(self, config_json: dict) -> str:
        """Retourne une URL directe (MP4 ou HLS) depuis le JSON de config du player."""
        try:
            files = config_json.get('request', {}).get('files', {})
            progressive = files.get('progressive') or []
            if isinstance(progressive, list) and progressive:
                # Choisir la plus haute résolution
                sorted_progressive = sorted(progressive, key=lambda f: f.get('height', 0), reverse=True)
                return sorted_progressive[0].get('url') or ''
            # HLS fallback
            hls_info = files.get('hls', {})
            if isinstance(hls_info, dict):
                if 'url' in hls_info and hls_info['url']:
                    return hls_info['url']
                cdns = hls_info.get('cdns', {})
                for _, cdn_info in cdns.items():
                    if 'url' in cdn_info and cdn_info['url']:
                        return cdn_info['url']
        except Exception:
            pass
        return ''

    def download_video(self, url: str) -> str:
        """
        Télécharge la vidéo Vimeo et retourne le chemin du fichier audio extrait (MP3 si possible).
        """
        if not self.validate_vimeo_url(url):
            raise ValueError('URL Vimeo invalide')

        try:
            # Normaliser l'URL pour éviter les problèmes d'OAuth sur les URLs player
            normalized_url = url
            m = re.search(r'(?:vimeo\.com/(?:.*?/)?(\d+)|player\.vimeo\.com/video/(\d+))', url)
            video_id = None
            if m:
                video_id = m.group(1) or m.group(2)
                normalized_url = f'https://vimeo.com/{video_id}'
            # Variantes d'URL à tenter, incluant une URL directe si disponible
            attempt_urls = []
            if video_id:
                config_json = self._fetch_player_config(video_id)
                direct_url = self._get_best_direct_url(config_json)
                if direct_url:
                    attempt_urls.append(direct_url)
            attempt_urls.append(normalized_url)
            if video_id:
                attempt_urls.append(f'https://player.vimeo.com/video/{video_id}')

            # Cloner les options et ajuster les en-têtes dynamiques
            opts = self.audio_opts.copy()
            headers = opts.get('http_headers', {}).copy()
            if video_id:
                headers['Referer'] = f'https://vimeo.com/{video_id}'
                headers['Origin'] = 'https://vimeo.com'
            opts['http_headers'] = headers

            filename = None
            last_err = None
            # 1) Tentatives avec différentes options et variantes d'URL
            option_attempts = [
                {'extractor_args': {'vimeo': {'use_api': ['no']}}},
                {'extractor_args': {'vimeo': {'use_api': ['no']}}, 'cookiesfrombrowser': ('safari',)},
                {'extractor_args': {'vimeo': {'use_api': ['no']}}, 'cookiesfrombrowser': ('chrome',)},
                {'force_generic_extractor': True},
            ]
            for attempt in option_attempts:
                for test_url in attempt_urls:
                    try:
                        attempt_opts = opts.copy()
                        attempt_opts.update(attempt)
                        with yt_dlp.YoutubeDL(attempt_opts) as ydl:
                            info = ydl.extract_info(test_url, download=True)
                            filename = ydl.prepare_filename(info)
                            break
                    except Exception as e:
                        last_err = e
                        continue
                if filename:
                    break
            if filename is None:
                raise last_err or Exception('Téléchargement Vimeo impossible (toutes les tentatives ont échoué)')

            # Remplacer l'extension d'origine par .mp3 si postprocessor exécuté
            audio_filename = os.path.splitext(filename)[0] + '.mp3'
            if os.path.exists(audio_filename):
                return audio_filename

            # Fallback: chercher formats audio alternatifs
            for ext in ['.m4a', '.webm', '.opus']:
                alt = os.path.splitext(filename)[0] + ext
                if os.path.exists(alt):
                    return alt

            # Dernier recours: retourner le fichier d'origine si présent
            if os.path.exists(filename):
                return filename

            raise Exception('Fichier audio non trouvé après extraction')
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement Vimeo: {str(e)}")

    def download_video_only(self, url: str) -> str:
        """Télécharge uniquement la vidéo Vimeo (retourne le chemin du fichier vidéo)."""
        if not self.validate_vimeo_url(url):
            raise ValueError('URL Vimeo invalide')

        try:
            # Normaliser l'URL pour éviter les problèmes d'OAuth sur les URLs player
            normalized_url = url
            m = re.search(r'(?:vimeo\.com/(?:.*?/)?(\d+)|player\.vimeo\.com/video/(\d+))', url)
            video_id = None
            if m:
                video_id = m.group(1) or m.group(2)
                normalized_url = f'https://vimeo.com/{video_id}'
            attempt_urls = [normalized_url]
            if video_id:
                attempt_urls.append(f'https://player.vimeo.com/video/{video_id}')

            # Cloner les options et ajuster les en-têtes dynamiques
            opts = self.video_opts.copy()
            headers = opts.get('http_headers', {}).copy()
            if video_id:
                headers['Referer'] = f'https://vimeo.com/{video_id}'
                headers['Origin'] = 'https://vimeo.com'
            opts['http_headers'] = headers

            filename = None
            last_err = None
            option_attempts = [
                {'extractor_args': {'vimeo': {'use_api': ['no']}}},
                {'extractor_args': {'vimeo': {'use_api': ['no']}}, 'cookiesfrombrowser': ('safari',)},
                {'extractor_args': {'vimeo': {'use_api': ['no']}}, 'cookiesfrombrowser': ('chrome',)},
                {'force_generic_extractor': True},
            ]
            for attempt in option_attempts:
                for test_url in attempt_urls:
                    try:
                        attempt_opts = opts.copy()
                        attempt_opts.update(attempt)
                        with yt_dlp.YoutubeDL(attempt_opts) as ydl:
                            info = ydl.extract_info(test_url, download=True)
                            filename = ydl.prepare_filename(info)
                            break
                    except Exception as e:
                        last_err = e
                        continue
                if filename:
                    break
            if filename is None:
                raise last_err or Exception('Téléchargement Vimeo impossible (toutes les tentatives ont échoué)')

            # Essayer plusieurs extensions vidéo possibles
            for ext in ['.mp4', '.webm', '.mkv', '.mov']:
                candidate = os.path.splitext(filename)[0] + ext
                if os.path.exists(candidate):
                    return candidate

            if os.path.exists(filename):
                return filename

            raise Exception('Fichier vidéo non trouvé après téléchargement')
        except Exception as e:
            raise Exception(f"Erreur lors du téléchargement de la vidéo Vimeo: {str(e)}")


