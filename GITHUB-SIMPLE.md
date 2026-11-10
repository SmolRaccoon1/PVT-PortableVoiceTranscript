# Obtenir le fichier EXE sans installer Python

1. Sur GitHub, cliquer sur **New repository**.
2. Nommer le dépôt `VoiceTranscript`, choisir **Private**, puis **Create repository**.
3. Dans le dépôt vide, cliquer sur **uploading an existing file**.
4. Décompresser cette archive sur le PC, puis glisser **tout son contenu**, y compris le dossier `.github`, dans la page GitHub.
5. Cliquer sur **Commit changes**.
6. Ouvrir l'onglet **Actions**.
7. À gauche, choisir **Build Windows portable EXE**.
8. Cliquer sur **Run workflow**, puis encore **Run workflow**.
9. Attendre environ 5 à 15 minutes, puis ouvrir l'exécution terminée.
10. En bas, section **Artifacts**, télécharger `VoiceTranscript-portable`.
11. Décompresser le ZIP et lancer `VoiceTranscript.exe`.

Aucune installation n'est nécessaire sur le PC qui utilisera l'application.
