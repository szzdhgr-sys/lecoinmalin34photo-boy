# Bot Telegram LE COIN MALIN 34 — V6

**Périmètre : bot Telegram seulement. Aucun changement au site lecoinmalin34.fr.**

## Pourquoi /start peut rester sans réponse

Le bot utilise le polling Telegram `getUpdates` et doit rester lancé comme un service Railway.
Vérifier dans cet ordre :

1. **Railway > Service du bot > Deployments** : un déploiement `Active` doit être visible.
2. **Logs Railway** : chercher `TELEGRAM BOT OK`. Si `BOT_TOKEN manquant` ou `invalide` apparaît, vérifier la variable privée `BOT_TOKEN` (ne jamais la publier).
3. Si les logs montrent **HTTP=409**, un autre service utilise le même token. Ne laisser qu'une instance active.
4. Si les logs montrent une erreur `getUpdates` liée à un webhook, le bot appelle `deleteWebhook` au démarrage.
5. Pour les nouvelles publications, vérifier que le bot est administrateur ou que le mode confidentialité du groupe est désactivé.
6. La commande Telegram `/ping` doit répondre ; `/start` doit ouvrir le catalogue. La route `/health` du service Railway doit retourner `ok: true`.

**La branche GitHub ne réactive pas à elle seule un service Railway arrêté : le déploiement doit être actif.**

## Variables Railway

- `BOT_TOKEN` : token du bot fourni par BotFather, secret obligatoire.
- `ADMIN_USER_ID` : identifiant Telegram numérique de l'administrateur, obligatoire pour `/indeximages` et l'arrêt des scans (plusieurs IDs possibles, séparés par une virgule).
- `SOURCE_CHAT` : ID numérique du supergroupe avec le préfixe `-100` ; à vérifier selon le groupe actuel. Si absent, fallback historique.
- `DATA_DIR=/data` avec un **Railway Volume monté sur /data** pour préserver catalogues et index après redéploiement.
- `PAGE_SIZE=8` (de 1 à 20), facultatif.
- `PORT` : fourni normalement par Railway.

## Nouveautés V6

- `/ping` : test rapide et durée de fonctionnement.
- `/help` : liste des commandes.
- `/health` : état non sensible du processus et du polling pour la supervision.
- Pages de catalogue plus légères (8 publications par défaut).
- IDs de copie triés et dédoublonnés, avec copie individuelle de secours.
- Résolution du chat source avant la vérification des permissions.
- `/indeximages` et `cancelscan` réservés aux administrateurs configurés.
- Tests automatiques de syntaxe et des helpers.

## Limitations

Cette mise à jour **n'a pas accès au token ni aux logs Railway**. Elle ne prouve donc pas que le bot de production soit de nouveau en ligne. Le modèle de reconnaissance d'images reste facultatif et dépend de la configuration du serveur.

## Validation

```sh
python -m compileall -q bot.py bot_v6.py
python -m unittest discover -s tests -v
```
