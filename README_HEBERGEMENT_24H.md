# Bot Telegram 24h/24 sans PC : Oracle Cloud Always Free (Ubuntu)

**Le site lecoinmalin34.fr n'est pas concerné.** Cette procédure démarre
le bot catalogue Telegram en continu sur sa propre machine virtuelle.
Un serveur distant est nécessaire pour que le bot réponde quand le PC est éteint.

## 1. Créer une VM Always Free

Sur https://signup.oraclecloud.com, créer un compte Oracle Cloud Free Tier.
Carte bancaire et numéro de téléphone peuvent être requis pour validation.
Un essai à crédits de 30 jours est **distinct** des ressources Always Free.
Choisir uniquement une ressource affichée « Always Free Eligible » (Ubuntu).
Les petites VM gratuites sont parfois indisponibles et peuvent être récupérées
si inactives. **Aucune garantie de disponibilité permanente.**
Ne jamais activer de ressource payante sans vérifier les limites et les tarifs.

Dans la Console, aller à Compute > Instances > Create instance, choisir une image
Ubuntu admissible Always Free. Enregistrer la clé privée SSH sur son ordinateur
(et ne l'envoyer à personne), noter l'adresse IP publique.
Pour un bot Telegram en polling, il n'est **pas nécessaire** d'ouvrir les ports
8080/80/443 : les connexions HTTPS sont sortantes.

## 2. Installer le bot depuis SSH (Ubuntu, utilisateur ubuntu)

Sur Windows PowerShell, se connecter avec la clé SSH :
\`\`\`powershell
ssh -i "CHEMIN_VERS_CLE_PRIVEE" ubuntu@ADRESSE_IP_VM
\`\`\`

Puis sur le serveur :
\`\`\`bash
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip
git clone --branch fix/telegram-bot-v6-stability-20261110 \
  https://github.com/szzdhgr-sys/lecoinmalin34photo-boy.git \
  ~/lecoinmalin34-bot
cd ~/lecoinmalin34-bot
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p data
cp deploy/private.env.example private.env
chmod 600 private.env
nano private.env
\`\`\`

Dans \`nano\`, remplacer **uniquement** le faux \`BOT_TOKEN\` par le token renouvelé
via @BotFather. Renseigner \`SOURCE_CHAT\` si le groupe a changé. Ne jamais envoyer
ce fichier ni son contenu à un chat, GitHub ou une capture d'écran.
Sauvegarder avec Ctrl+O et Entrée, fermer avec Ctrl+X.

Tester les fichiers sans lancer deux copies en même temps :
\`\`\`bash
.venv/bin/python -m compileall -q bot.py bot_v6.py bot_v7_search.py bot_runtime.py
.venv/bin/python -m unittest discover -s tests -v
\`\`\`

## 3. Démarrage automatique après reboot

Arrêter **l'ancienne fenêtre du bot Windows** (Ctrl+C) : un token ne peut pas
être utilisé simultanément par deux pollers, sinon Telegram renvoie HTTP 409.

Puis sur la VM :
\`\`\`bash
sudo cp deploy/lecoinmalin34-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now lecoinmalin34-bot
sudo systemctl status lecoinmalin34-bot --no-pager
journalctl -u lecoinmalin34-bot -n 40 --no-pager
\`\`\`

La ligne \`TELEGRAM BOT OK\` confirme la vérification auprès de Telegram.
\`SOURCE OK\` confirme l'identifiant du groupe. Puis tester /start sur le bot.
Le système redémarre le service automatiquement après un reboot.

## 4. Synchronisation automatique des nouveaux produits

Le bot doit être administrateur du supergroupe catalogue (ou disposer d'un mode
confidentialité désactivé) pour recevoir les photos/vidéos publiées.
Le post doit être publié dans **un topic du groupe source**. Le bot ajoute
automatiquement son identifiant Telegram dans la rubrique correspondante et
dans Nouveautés. Pour que la recherche par marque fonctionne aussi, inclure
la marque et le modèle dans la légende, par exemple « Nike Air Max - 42 ».

Après avoir posté un produit, vérifier les journaux :
\`\`\`bash
journalctl -u lecoinmalin34-bot -f
\`\`\`
Chercher « TELEGRAM UPDATES queued », « AUTO AJOUT » ; tester /start, la rubrique,
Nouveautés et /recherche sur Telegram. La mise à jour est prévue sans
redémarrage ni transfert manuel des photos.

En cas de coupure passagère, le bot dispose maintenant d'une file SQLite locale
(\`data/telegram_updates.sqlite3\`) qui sauvegarde les updates reçues avant
leur traitement. Elle ne remplace pas les sauvegardes et ne peut pas récupérer
des événements jamais livrés par Telegram pendant une longue interruption.

## 5. Sécurité et entretien

- Sauvegarder régulièrement \`data/\`, notamment le catalogue et la file SQLite.
- Ne jamais partager \`private.env\`, un token, ou la clé privée SSH.
- Ne pas utiliser l'ancien token divulgué : @BotFather > /revoke.
- Ne pas lancer simultanément le bot sur Windows et sur Oracle Cloud.
- Si le nom d'utilisateur est différent (\`opc\` au lieu de \`ubuntu\`), adapter
  \`User=\`, \`WorkingDirectory=\` et \`ExecStart=\` dans le service.
- Pour un vrai service commercial avec disponibilité garantie, prévoir un
  VPS payant et des sauvegardes : les VM Always Free ne garantissent pas 100 % uptime.

Sources officielles :
- https://docs.oracle.com/fr-fr/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm
- https://docs.oracle.com/fr-fr/iaas/Content/GSG/Tasks/signingup_topic-Sign_Up_for_Free_Oracle_Cloud_Promotion.htm
- https://docs.oracle.com/fr-fr/iaas/Content/Compute/tutorials/first-linux-instance/overview.htm
