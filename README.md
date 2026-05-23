# SRV-INTRANET — Site intranet interne (Flask + Gunicorn + Nginx)

| Paramètre | Valeur |
|---|---|
| **Hostname** | SRV-INTRANET |
| **FQDN** | intranet.itway.local |
| **OS** | Debian 12.6 Bookworm |
| **IP** | 10.0.4.5 / 27 |
| **Passerelle** | 10.0.4.1 |
| **DNS** | 10.0.4.2 (SRV-ADS01) |
| **VLAN** | SRV-VLAN |

---

## Contenu du dossier

```
srv-intranet/
├── README.md
├── hosts.ini
├── playbook_srv_intranet.yml
├── Vagrantfile
└── app/
    ├── app.py                 ← Application Flask principale
    ├── .env.example           ← Template des variables d'environnement (sans secrets)
    ├── templates/
    │   ├── base.html
    │   └── index.html
    └── static/
        ├── style.css
        └── accessibility.css  ← Fonctionnalité accessibilité
```

---

## Stack technique

| Composant | Rôle | Port |
|---|---|---|
| Flask (Python 3) | Framework web | — |
| Gunicorn | Serveur WSGI (3 workers) | 5000 (local) |
| Nginx | Reverse proxy + SSL | 80 / 443 |
| SQLite | Base de données actualités | local |

---

## Ce que fait le playbook

- Installation des paquets (python3, venv, nginx, ufw, sqlite3)
- Création de l'utilisateur système `intranet` (sans shell)
- Création des répertoires `/opt/intranet/`
- Création du virtualenv Python + installation des dépendances (flask, gunicorn, authlib, flask-login, requests)
- Déploiement du service systemd `intranet`
- Configuration Nginx (reverse proxy HTTP + HTTPS avec certificat PKI)
- Configuration UFW (SSH IT, HTTP/HTTPS tous internes)

---

## Déploiement

```bash
ansible-playbook -i hosts.ini playbook_srv_intranet.yml
```

### Déploiement des fichiers applicatifs (manuel)

```bash
sudo nano /opt/intranet/app/app.py
sudo nano /opt/intranet/app/.env
sudo nano /opt/intranet/app/templates/base.html
sudo nano /opt/intranet/app/templates/index.html
sudo nano /opt/intranet/app/static/style.css
sudo nano /opt/intranet/app/static/accessibility.css

sudo systemctl restart intranet
sudo systemctl status intranet
```

---

## Variables d'environnement (`.env`)

```bash
# Copier le fichier exemple et remplir les valeurs
cp .env.example .env
```

| Variable | Description |
|---|---|
| `FLASK_SECRET_KEY` | Clé secrète Flask (générée aléatoirement) |
| `KEYCLOAK_URL` | URL du SSO (ex: `https://sso.itway.local`) |
| `KEYCLOAK_REALM` | Nom du realm (ex: `itway`) |
| `KEYCLOAK_CLIENT_ID` | `intranet-client` |
| `KEYCLOAK_CLIENT_SECRET` | Secret OIDC (voir console Keycloak) |
| `KEYCLOAK_REDIRECT_URI` | `https://intranet.itway.local/auth/callback` |
| `DATABASE` | `/opt/intranet/app/intranet.db` |

---

## Flux d'authentification OIDC

```
1. Utilisateur → https://intranet.itway.local
2. Flask détecte session absente → redirige vers Keycloak
3. Keycloak authentifie via Active Directory (+ MFA OTP)
4. Keycloak délivre un jeton OIDC (Authorization Code flow)
5. Flask valide via /userinfo → ouvre session
6. Affichage des actualités triées par date
```

---

## Gestion des actualités (SQLite)

```bash
# Se connecter à la base
sudo sqlite3 /opt/intranet/app/intranet.db

# Ajouter une actualité
INSERT INTO news (title, content, author) VALUES ('Titre', 'Contenu', 'Auteur');
.quit

# Supprimer une actualité (remplacer ** par l'ID)
sudo sqlite3 /opt/intranet/app/intranet.db "DELETE FROM news WHERE id = **;"
```

---

## Pare-feu UFW

| Source | Port | Usage |
|---|---|---|
| IT-VLAN (10.0.3.0/28) | 22 | SSH admin + Ansible |
| Tous internes (10.0.0.0/8) | 80 / 443 | Accès intranet |

---

## Points à traiter

- [ ] Ajouter une interface web d'administration des actualités
