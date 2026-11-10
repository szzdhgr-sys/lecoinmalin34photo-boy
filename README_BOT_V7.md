# LE COIN MALIN 34 — Bot Telegram V7 (sans changement du site)

Cette branche modifie **seulement le bot Telegram**, pas \`lecoinmalin34.fr\`.
La branche est une proposition : **elle n'est pas déployée automatiquement**.

## Interface demandée

- Accueil : bouton **🔎 Rechercher un produit / une marque**.
- \`/recherche\` : cherche dans toutes les catégories : produit, modèle, marque, expression.
- Choix d'une grande rubrique (vêtements, chaussures, high-tech, montres, accessoires...) : liste des sous-rubriques.
- Choix d'une sous-rubrique : **marques trouvées dans les légendes**, puis boutons
  **🔎 Rechercher un article / modèle** et **📷 Tous les articles**.
- Sélection d'une marque : n'envoie que les messages de cette marque dans cette rubrique.
- Affichage paginé (8 par défaut) avec précédent/suivant. Les résultats d'une recherche sont spécifiques à la conversation privée.
- Nouveaux posts et légendes du groupe source : indexation automatique.
- Ancien export \`result.json\` / \`result(2).json\` : indexation des légendes au démarrage.

**Important :** une photo/vidéo sans légende identifiable ne permet pas
de trouver honnêtement sa marque. Les photos sans texte restent dans
**Tous les articles**. Les noms affichés ne vérifient pas l'authenticité des marques.
Le bouton « rechercher » demande à l'utilisateur d'écrire dans le champ normal
du chat Telegram ; la Bot API ne permet pas d'insérer une véritable barre de
recherche native personnalisée en haut d'une conversation.

## Commandes

\`/start\` : menu ; \`/recherche\` : recherche globale ; \`/ping\` : vérification ;
\`/status\` : informations de synchronisation ; \`/id\` : votre identifiant Telegram ;
\`/help\` : commandes ; \`/cancel\` : annuler.

Pour les fonctions administrateur : définir \`ADMIN_USER_ID\` avant d'utiliser
\`/indeximages\`. Ne pas mettre de token dans GitHub.

## Installer sans Railway : ordinateur Windows 10/11

1. Sur GitHub, télécharger le code de la branche ou fusionner la pull request puis
   faire « Code > Download ZIP » ; décompresser.
2. Installer Python 3 avec la commande \`py -3 --version\` disponible.
3. Copier \`bot-private.example.cmd\` vers \`bot-private.cmd\`, renseigner le token
   BotFather et son ID Telegram après la commande \`/id\` (au besoin ID obtenu
   dans l'ancienne version ou autre méthode).
4. Double-cliquer \`run_bot_windows.bat\`. Il installe les dépendances puis lance
   le bot. Pour rester disponible, le PC **doit rester allumé**, ne pas se mettre en veille.
5. Le répertoire \`data\` est conservé entre les redémarrages. Sauvegarder ce
   répertoire et le fichier local privé en sécurité.

**Attention : ne jamais lancer simultanément deux copies du même bot** avec
un seul token, sinon Telegram renvoie HTTP 409.

## Option serveur Linux 24h/24

Le même code fonctionne avec Python 3.11+ sur une petite VM Linux.
Sur un VPS, lancer \`python bot.py\` comme service \`systemd\` avec
\`WorkingDirectory\` pointant vers le dépôt, et un fichier \`EnvironmentFile\`
privé pour \`BOT_TOKEN\`, \`ADMIN_USER_ID\`, \`SOURCE_CHAT\` et \`DATA_DIR\`.
Installer avec \`pip install -r requirements.txt\`.

Choisir un disque persistant pour \`DATA_DIR\`.
- **Oracle Cloud Always Free** : pas limité aux 30 jours d'essai, mais
  inscription et carte bancaire requises ; disponibilité variable,
  ressources inactives récupérables.
- **VPS payant** : solution généralement plus prévisible.
- Services Web « gratuits » avec mise en veille : **pas adaptés au polling**
  en permanence. Ne pas compter sur Render Free ou Koyeb Free pour du 24/7.

## Avant le déploiement

\`\`\`sh
python -m compileall -q bot.py bot_v6.py bot_v7_search.py
python -m unittest discover -s tests -v
\`\`\`

Contrôler les logs : \`TELEGRAM BOT OK\`, \`SOURCE OK\`, \`SEARCH INDEX\`.
Puis tester \`/ping\`, \`/start\`, \`/recherche\`, une marque dans chaque rubrique.
Le diagnostic de la panne précédente exige toujours les logs de l'hébergeur.

## Mode vitrine uniquement

Le bot V7 sert uniquement à consulter les produits (photos/vidéos, catégories, marques, recherche). Il ne propose aucune prise de commande, aucun panier et aucun paiement. Les anciens messages du groupe peuvent contenir des informations historiques, mais les interfaces publiques du bot n'affichent pas de bouton « Commander ».

La variable `ADMIN_USER_ID` est **facultative**. Sans cette variable, les fonctions de scan administrateur restent désactivées ; les visiteurs peuvent quand même utiliser les rubriques, filtres et recherches.
