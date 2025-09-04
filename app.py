import os
import json
from flask import Flask, render_template, request, jsonify, send_file
from instagram_downloader import InstagramDownloader
from tiktok_downloader import TikTokDownloader
from vimeo_downloader import VimeoDownloader
from transcriber import AudioTranscriber
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialisation des modules
instagram_downloader = InstagramDownloader()
tiktok_downloader = TikTokDownloader()
vimeo_downloader = VimeoDownloader()
transcriber = AudioTranscriber()

@app.route('/')
def index():
    """Page d'accueil avec le formulaire"""
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_social_video():
    """Endpoint principal pour transcription des vidéos Instagram et TikTok"""
    try:
        # Récupération de l'URL depuis la requête JSON
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL manquante'
            }), 400
        
        # Déterminer le type de plateforme et valider l'URL
        if instagram_downloader.validate_instagram_url(url):
            downloader = instagram_downloader
            platform = 'Instagram'
        elif tiktok_downloader.validate_tiktok_url(url):
            downloader = tiktok_downloader
            platform = 'TikTok'
        elif vimeo_downloader.validate_vimeo_url(url):
            downloader = vimeo_downloader
            platform = 'Vimeo'
        else:
            return jsonify({
                'success': False,
                'error': "URL invalide. Veuillez utiliser une URL Instagram, TikTok ou Vimeo valide."
            }), 400
        
        # Étape 1: Téléchargement de la vidéo
        try:
            audio_file_path = downloader.download_video(url)
            if not audio_file_path or not os.path.exists(audio_file_path):
                raise Exception("Impossible de télécharger la vidéo")
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erreur de téléchargement: {str(e)}'
            }), 500
        
        # Étape 2: Transcription avec Whisper
        try:
            # Utilisation de la transcription avec détection de langue
            result = transcriber.transcribe_with_language_detection(audio_file_path)
            transcript_text = result['text']
            detected_language = result.get('language', 'Non détectée')
            
        except Exception as e:
            # Si la transcription avec détection de langue échoue, essaie la version simple
            try:
                transcript_text = transcriber.transcribe_audio(audio_file_path)
                detected_language = 'Auto-détectée'
            except Exception as e2:
                return jsonify({
                    'success': False,
                    'error': f'Erreur de transcription: {str(e2)}'
                }), 500
        
        # Étape 3: Nettoyage des fichiers temporaires
        try:
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
        except Exception:
            pass  # Ignore les erreurs de nettoyage
        
        # Retour du résultat
        return jsonify({
            'success': True,
            'transcript': transcript_text,
            'language': detected_language,
            'url': url
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur générale: {str(e)}'
        }), 500

@app.route('/download', methods=['POST'])
def download_social_video():
    """Endpoint pour télécharger les vidéos Instagram et TikTok"""
    try:
        # Récupération de l'URL depuis la requête JSON
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL manquante'
            }), 400
        
        # Déterminer le type de plateforme et valider l'URL
        if instagram_downloader.validate_instagram_url(url):
            downloader = instagram_downloader
            platform = 'Instagram'
        elif tiktok_downloader.validate_tiktok_url(url):
            downloader = tiktok_downloader
            platform = 'TikTok'
        elif vimeo_downloader.validate_vimeo_url(url):
            downloader = vimeo_downloader
            platform = 'Vimeo'
        else:
            return jsonify({
                'success': False,
                'error': "URL invalide. Veuillez utiliser une URL Instagram, TikTok ou Vimeo valide."
            }), 400
        
        # Téléchargement de la vidéo (sans extraction audio)
        try:
            video_file_path = downloader.download_video_only(url)
            if not video_file_path or not os.path.exists(video_file_path):
                raise Exception("Impossible de télécharger la vidéo")
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Erreur de téléchargement: {str(e)}'
            }), 500
        
        # Retourner le fichier pour téléchargement
        try:
            # Détecter l'extension et choisir le bon mimetype
            _, ext = os.path.splitext(video_file_path)
            ext = ext.lower() or '.mp4'
            mimetypes = {
                '.mp4': 'video/mp4',
                '.webm': 'video/webm',
                '.mkv': 'video/x-matroska',
                '.mov': 'video/quicktime',
            }
            mime = mimetypes.get(ext, 'application/octet-stream')

            response = send_file(
                video_file_path,
                as_attachment=True,
                download_name=f'{platform.lower()}_video{ext}',
                mimetype=mime
            )
            
            # Programmer la suppression du fichier après l'envoi
            @response.call_on_close
            def cleanup():
                try:
                    if os.path.exists(video_file_path):
                        os.remove(video_file_path)
                except Exception:
                    pass
            
            return response
            
        except Exception as e:
            # Nettoyage en cas d'erreur
            try:
                if os.path.exists(video_file_path):
                    os.remove(video_file_path)
            except Exception:
                pass
            
            return jsonify({
                'success': False,
                'error': f'Erreur lors de l\'envoi du fichier: {str(e)}'
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Erreur générale: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """Endpoint de vérification de santé de l'application"""
    return jsonify({
        'status': 'OK',
        'service': 'Social Media Tool',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint non trouvé'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Erreur interne du serveur'
    }), 500

if __name__ == '__main__':
    # Création du dossier de téléchargement si nécessaire
    os.makedirs(Config.DOWNLOAD_FOLDER, exist_ok=True)

    # Port dynamique pour environnements managés (Render fournit $PORT)
    port = int(os.environ.get('PORT', 5001))

    print("🚀 Démarrage du serveur Social Media Tool...")
    print(f"📱 Accédez à http://localhost:{port} pour utiliser l'application")
    print("🔑 Clé API configurée et prête à utiliser")
    print("✨ Fonctionnalités: Transcription + Téléchargement de vidéos")
    print("🌐 Plateformes supportées: Instagram, TikTok et Vimeo")

    app.run(debug=True, host='0.0.0.0', port=port)