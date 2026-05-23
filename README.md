# SRV-PKI — Autorité de certification interne (Root CA)

| Paramètre | Valeur |
|---|---|
| **Hostname** | SRV-PKI |
| **FQDN** | srv-pki.itway.local |
| **OS** | Debian 12.6 Bookworm |
| **IP** | 10.0.4.3 / 27 |
| **Passerelle** | 10.0.4.1 |
| **DNS** | 10.0.4.2 (SRV-ADS01) |
| **VLAN** | SRV-VLAN |

---

## Contenu du dossier

```
srv-pki/
├── README.md
├── hosts.ini                  ← Inventaire Ansible
├── playbook_srv_pki.yml       ← Déploiement complet de la CA
└── openssl.cnf                ← Configuration OpenSSL de la CA
```

---

## Ce que fait le playbook

- Installation des paquets (openssl, apache2, ufw, cron)
- Configuration réseau statique (eth0)
- Configuration UFW (SSH IT+SRV, HTTP tous internes)
- Création de l'arborescence `/etc/pki/` (certs, crl, newcerts, private, secrets)
- Génération de la clé privée RSA 4096 bits chiffrée AES256
- Génération du certificat CA auto-signé (valide 10 ans)
- Génération de la CRL initiale
- Configuration Apache2 pour publication HTTP de la CRL et du certificat CA
- Cron de renouvellement automatique de la CRL (tous les 15 jours à 3h)
- Installation du certificat CA dans le store système

---

## Déploiement

```bash
ansible-playbook -i hosts.ini playbook_srv_pki.yml
```

---

## CA — Caractéristiques

| Paramètre | Valeur |
|---|---|
| Type | Root CA (auto-signée) |
| Algorithme | RSA 4096 bits |
| Chiffrement clé | AES256 |
| Hash | SHA-256 |
| Validité CA | 10 ans (3650 jours) |
| Validité certificats signés | 1 an (365 jours) |
| Validité CRL | 30 jours (renouvelée tous les 15 jours) |
| Numéro de série initial | 1000 |
| Organisation | ITWay / FR / PACA |

---

## Arborescence `/etc/pki/`

```
/etc/pki/
├── certs/         ← Certificats CA + serveurs signés
│   └── ca.crt
├── crl/           ← Liste de révocation
│   └── ca.crl
├── newcerts/      ← Archive des certificats émis
├── private/       ← Clés privées (mode 700)
│   └── ca.key     ← Clé CA (mode 400, root uniquement)
├── secrets/       ← Passphrase CA (mode 700)
├── index.txt      ← Base de données des certificats
├── serial         ← Numéro de série courant
└── openssl.cnf    ← Configuration OpenSSL
```

---

## URLs de publication

| Ressource | URL |
|---|---|
| Certificat CA | `http://srv-pki.itway.local/certs/ca.crt` |
| CRL | `http://srv-pki.itway.local/crl/ca.crl` |

---

## Certificats déjà émis

| Certificat | Déployé sur | Statut |
|---|---|---|
| `sso.itway.local` | SRV-SSO `/etc/nginx/ssl/` | ✅ Actif |
| `intranet.itway.local` | SRV-INTRANET `/etc/nginx/ssl/` | ✅ Actif |

---

## Générer un nouveau certificat serveur

```bash
# 1. Générer la clé privée du serveur
openssl genrsa -out /etc/pki/private/<nom>.key 2048

# 2. Générer la CSR
openssl req -new -key /etc/pki/private/<nom>.key \
  -out /etc/pki/certs/<nom>.csr \
  -subj "/C=FR/ST=PACA/L=Avignon/O=ITWay/CN=<fqdn>"

# 3. Signer avec la CA (demande la passphrase)
openssl ca -config /etc/pki/openssl.cnf \
  -in /etc/pki/certs/<nom>.csr \
  -out /etc/pki/certs/<nom>.crt \
  -days 365

# 4. Transférer le certificat sur le serveur cible
scp /etc/pki/certs/<nom>.crt ansible@<ip>:/etc/nginx/ssl/
scp /etc/pki/private/<nom>.key ansible@<ip>:/etc/nginx/ssl/
```

---

## Points à traiter

- [ ] Passer les secrets CA dans **Ansible Vault** (passphrase actuellement en clair dans le playbook)
- [ ] Émettre les certificats pour les services restants (LDAPS, DMZ-MAIL, DMZ-WEB)
- [ ] Déployer un répondeur **OCSP** si requis (port 2560)
