# 🎬 Transcripteur Social (Instagram, TikTok, Vimeo)

Un outil puissant pour télécharger et transcrire automatiquement des vidéos Instagram, TikTok et Vimeo en utilisant l'intelligence artificielle.

## ✨ Fonctionnalités

- **Téléchargement automatique** : Extrait l'audio des vidéos Instagram, TikTok et Vimeo
- **Transcription IA** : Utilise OpenAI Whisper pour une transcription précise
- **Détection de langue** : Reconnaît automatiquement la langue parlée
- **Interface moderne** : Application web intuitive et responsive
- **Traitement rapide** : Résultats en quelques minutes

## 🚀 Installation

### Prérequis

- Python 3.8 ou plus récent
- Une clé API OpenAI
- ffmpeg (pour le traitement audio)

### Installation de ffmpeg

**Sur macOS :**
```bash
brew install ffmpeg
```

**Sur Ubuntu/Debian :**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Sur Windows :**
Téléchargez depuis [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### Installation du projet

1. **Clonez ou téléchargez le projet**
   ```bash
   cd "transcript insta"
   ```

2. **Installez les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurez votre clé API OpenAI**
   
   La clé API est déjà configurée dans le fichier `config.py`. Si vous souhaitez utiliser une autre clé, modifiez la ligne :
   ```python
   OPENAI_API_KEY = "votre_nouvelle_cle_api"
   ```

## 🎯 Utilisation

### Démarrage de l'application

```bash
python app.py
```

L'application sera accessible à l'adresse : **http://localhost:5000**

### Utilisation de l'interface web

1. **Ouvrez votre navigateur** et allez sur `http://localhost:5000`
2. **Collez l'URL du réel Instagram** dans le champ prévu
3. **Cliquez sur "Générer la transcription"**
4. **Attendez le traitement** (quelques minutes selon la longueur)
5. **Récupérez votre transcription** avec la langue détectée

### Formats d'URL supportés

- Instagram: `https://www.instagram.com/reel/ABC123/`, `https://instagram.com/reel/ABC123/`, `https://www.instagram.com/p/ABC123/`
- TikTok: `https://www.tiktok.com/@username/video/1234567890`, `https://vm.tiktok.com/xxxxx/`
- Vimeo: `https://vimeo.com/123456789`, `https://player.vimeo.com/video/123456789`

## 📁 Structure du projet

```
transcript-insta/
├── app.py                 # Application Flask principale
├── config.py              # Configuration et clé API
├── instagram_downloader.py # Module de téléchargement
├── transcriber.py         # Module de transcription
├── requirements.txt       # Dépendances Python
├── templates/
│   └── index.html        # Interface utilisateur
├── vimeo_downloader.py   # Module de téléchargement Vimeo
├── downloads/            # Dossier temporaire (créé automatiquement)
└── README.md             # Ce fichier
```

## 🔧 Configuration avancée

### Variables d'environnement

Vous pouvez créer un fichier `.env` pour une configuration plus sécurisée :

```bash
OPENAI_API_KEY=votre_cle_api_openai
DOWNLOAD_FOLDER=downloads
```

### Personnalisation

- **Dossier de téléchargement** : Modifiez `DOWNLOAD_FOLDER` dans `config.py`
- **Qualité audio** : Ajustez `preferredquality` dans `instagram_downloader.py`
- **Port du serveur** : Changez le port dans `app.py` (ligne finale)

## 🛠️ Dépannage

### Erreurs courantes

**"Erreur de téléchargement"**
- Vérifiez que l'URL Instagram est correcte et publique
- Assurez-vous que ffmpeg est installé

**"Erreur de transcription"**
- Vérifiez votre clé API OpenAI
- Assurez-vous d'avoir du crédit sur votre compte OpenAI

**"Impossible d'installer yt-dlp"**
```bash
pip install --upgrade yt-dlp
```

### Logs de débogage

Démarrez l'application avec plus de détails :
```bash
python app.py --debug
```

## 📝 API

### Endpoint de transcription

**POST** `/transcribe`

```json
{
  "url": "https://www.instagram.com/reel/ABC123/"
}
```

**Réponse réussie :**
```json
{
  "success": true,
  "transcript": "Texte transcrit de la vidéo...",
  "language": "fr",
  "url": "https://www.instagram.com/reel/ABC123/"
}
```

**Réponse d'erreur :**
```json
{
  "success": false,
  "error": "Description de l'erreur"
}
```

### Endpoint de santé

**GET** `/health`
```json
{
  "status": "OK",
  "service": "Instagram Transcriber",
  "version": "1.0.0"
}
```

## ⚠️ Limitations

- **Vidéos publiques uniquement** : Les comptes privés ne sont pas supportés
- **Taille de fichier** : Limitée par les quotas OpenAI (25 MB max)
- **Durée** : Recommandé pour des vidéos de moins de 10 minutes
- **Langues** : Toutes les langues supportées par Whisper

## 🔒 Sécurité

- **Clé API** : Ne partagez jamais votre clé OpenAI
- **Fichiers temporaires** : Automatiquement supprimés après traitement
- **HTTPS** : Recommandé pour un déploiement en production

## 🤝 Support

Pour toute question ou problème :
1. Vérifiez ce README
2. Consultez les logs d'erreur
3. Assurez-vous que toutes les dépendances sont installées

## 📄 Licence

Ce projet est fourni tel quel pour un usage personnel et éducatif.

---

**Note :** Respectez les conditions d'utilisation d'Instagram et d'OpenAI lors de l'utilisation de cet outil. 