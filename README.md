# SRV-SSO — Identity Provider centralisé (Keycloak 24.0.4)

| Paramètre | Valeur |
|---|---|
| **Hostname** | SRV-SSO |
| **FQDN interne** | sso.itway.local |
| **FQDN externe** | sso.itway.fr |
| **OS** | Debian 12.6 Bookworm |
| **IP** | 10.0.4.4 / 27 |
| **Passerelle** | 10.0.4.1 |
| **DNS** | 10.0.4.2 (SRV-ADS01) |
| **VLAN** | SRV-VLAN |
| **RAM** | 4 Go |
| **CPU** | 2 vCPU |

---

## Contenu du dossier

```
srv-sso/
├── README.md
├── hosts.ini                  ← Inventaire Ansible
├── playbook_srv_sso.yml       ← Déploiement Keycloak
├── keycloak.conf              ← Configuration Keycloak (sans secrets)
└── vagrantfile
```

---

## Stack technique

| Composant | Version | Port |
|---|---|---|
| Keycloak | 24.0.4 | 8080 (interne) |
| PostgreSQL | 15+ | 5432 (local) |
| Nginx | 1.22+ | 80 / 443 |
| OpenJDK | 17 | — |

---

## Ce que fait le playbook

- Mise à jour système et installation des paquets (Java, PostgreSQL, Nginx, UFW)
- Configuration UFW
- Création base de données et utilisateur PostgreSQL
- Téléchargement et extraction de Keycloak 24.0.4
- Création de l'utilisateur système `keycloak`
- Déploiement de `keycloak.conf`
- Build Keycloak (optimisation Quarkus)
- Création et activation du service systemd
- Configuration Nginx reverse proxy (HTTP + HTTPS)
- Installation du certificat CA ITWay dans le store système

### Configuration manuelle post-déploiement (interface web)
Les étapes suivantes sont effectuées manuellement depuis `https://sso.itway.local/admin` :
1. Création du realm `itway`
2. Configuration de la fédération LDAP avec SRV-ADS01
3. Synchronisation des 8 utilisateurs AD
4. Création du client OIDC `intranet-client`
5. Création du client OIDC `wordpress-client`
6. Activation du MFA / OTP (forcé à la première connexion)

---

## Déploiement

```bash
ansible-playbook -i hosts.ini playbook_srv_sso.yml
```

---

## Fédération LDAP

| Paramètre | Valeur |
|---|---|
| Protocole | LDAP (port 389) — LDAPS prévu |
| Serveur AD | 10.0.4.2 (SRV-ADS01) |
| Bind DN | `CN=svc-keycloak,OU=Services,OU=ITWay,DC=ITway,DC=local` |
| Users DN | `OU=Utilisateurs,OU=ITWay,DC=ITway,DC=local` |
| Mode | READ_ONLY |
| Utilisateurs synchronisés | 8 |

---

## Clients OIDC

| Client ID | Redirect URI | Application |
|---|---|---|
| `intranet-client` | `https://intranet.itway.local/*` | SRV-INTRANET |
| `wordpress-client` | `https://sso.itway.fr/*` | DMZ-WEB |


---

## Pare-feu UFW

| Source | Port | Usage |
|---|---|---|
| IT-VLAN (10.0.3.0/28) | 22 | SSH admin + Ansible |
| IT-VLAN + SRV-VLAN | 8080 | Console admin Keycloak |
| Tous internes (10.0.0.0/8) | 80 / 443 | Endpoints OIDC |

---

## Maintenance

```bash
# État des services
systemctl status keycloak nginx postgresql

# Logs Keycloak
tail -f /var/log/keycloak/keycloak.log
journalctl -u keycloak -f

# Redémarrage
sudo systemctl restart keycloak nginx

# Synchronisation manuelle des users LDAP
# → Console admin > realm itway > User Federation > ldap-provider > Synchronize all users

# Sauvegarde base de données
sudo -u postgres pg_dump keycloak > backup_keycloak_$(date +%Y%m%d).sql
```

---

## Points à traiter

- [ ] Déployer le **pont Kerberos / SPNEGO** (auth transparente intranet + WordPress)
