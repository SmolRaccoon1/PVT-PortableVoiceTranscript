# VoiceTranscript portable (Windows 10/11)

## Utilisation finale
1. Extraire `VoiceTranscript-portable.zip`.
2. Lancer `VoiceTranscript.exe`.
3. Raccourcis globaux :
   - `Ctrl+Alt+R` : démarrer / arrêter
   - `Ctrl+Alt+P` : pause / reprise
   - `Ctrl+Alt+Q` : quitter

Un indicateur semi-transparent s'affiche en bas à droite avec l'état et la durée.
Les fichiers sont créés dans `Transcripts`.

## Construire une fois
Sur un PC Windows avec Python 3.11 installé, double-cliquer sur `build.bat`. Le ZIP produit est ensuite portable et ne nécessite aucune installation.

## Limites
- Windows uniquement, sortie audio principale WASAPI et microphone Windows par défaut.
- Le premier build télécharge le modèle Whisper `small` (~500 Mo).
- Prévenir les participants et respecter les règles internes avant tout enregistrement.
