# ITWay SAS - Infrastructure DMZ
## Vagrantfiles + Ansible Playbooks

---

## Plan d'adressage (source : tableau officiel ITWay)

| VLAN       | Réseau/CIDR       | Gateway       | Description               |
|------------|-------------------|---------------|---------------------------|
| CORE-VLAN  | 10.0.10.0/30      | 10.0.10.1     | Interconnexion cœur réseau|
| SRV-VLAN   | 10.0.4.0/27       | 10.0.4.1      | Serveurs internes         |
| DMZ-VLAN   | 10.0.5.0/28       | 10.0.5.1      | Zone démilitarisée        |
| IT-VLAN    | 10.0.3.0/28       | 10.0.3.1      | Équipe informatique       |
| LAN-VLAN   | 192.168.15.0/24   | 192.168.15.1  | Réseau utilisateurs       |

---

## Adresses machines DMZ (10.0.5.0/28)

| Machine    | IP         | Hostname                          | Rôle                        |
|------------|------------|-----------------------------------|-----------------------------|
| RT-DMZ     | 10.0.5.1   | dmz-rt.int.itway.fr (gateway)     | Routeur Stormshield DMZ     |
| PROXY-DMZ  | 10.0.5.2   | proxy-dmz.int.itway.fr            | Reverse Proxy NGINX         |
| WEB-DMZ    | 10.0.5.3   | dmz-web.int.itway.fr              | WordPress (NGINX + PHP)     |
| MAIL-DMZ   | 10.0.5.4   | mail.itway.fr                     | Mailcow (Docker)            |
| DNS-DMZ    | 10.0.5.5   | dns.itway.fr                      | BIND9 autoritaire           |

## Adresses SRV-VLAN référencées (10.0.4.0/27)

| Machine     | IP        | Rôle                    |
|-------------|-----------|-------------------------|
| AD-SRV      | 10.0.4.2  | Active Directory / DNS  |
| PKI-SRV     | 10.0.4.3  | Autorité de certification|
| SSO-SRV     | 10.0.4.4  | Keycloak (OIDC/LDAP)    |
| INTRANET-SRV| 10.0.4.5  | Intranet interne        |

## IT-VLAN (10.0.3.0/28)

| Machine     | IP        | Rôle                    |
|-------------|-----------|-------------------------|
| ANSIBLE-IT  | 10.0.3.2  | Serveur Ansible         |

---

## Structure du dépôt

```
itway-dmz/
├── vagrantfiles/
│   ├── dmz-mail/Vagrantfile       # MAIL-DMZ  10.0.5.4
│   ├── dmz-rproxy/Vagrantfile     # PROXY-DMZ 10.0.5.2
│   ├── dmz-web/Vagrantfile        # WEB-DMZ   10.0.5.3
│   └── dmz-dns/Vagrantfile        # DNS-DMZ   10.0.5.5
└── ansible/
    ├── ansible.cfg
    ├── inventory/hosts
    ├── group_vars/
    │   ├── dmz.yml                # Variables communes (IPs, domaines)
    │   └── dmz_vault.yml          # Secrets (chiffrer avec ansible-vault !)
    ├── playbooks/
    │   └── dmz.yml                # Playbook principal
    └── roles/
        ├── dmz-mail/              # Docker + Mailcow (SMTP/IMAP/Webmail)
        ├── dmz-rproxy/            # NGINX Reverse Proxy (3 vhosts)
        ├── dmz-web/               # NGINX + PHP 8.2 + WordPress + OIDC
        └── dmz-dns/               # BIND9 (itway.fr + int.itway.fr)
```

---

## Prérequis sur ANSIBLE-IT (10.0.3.2)

```bash
pip3 install ansible

ansible-galaxy collection install \
  community.general \
  community.mysql \
  ansible.posix
```

---

## Certificats TLS à déposer (depuis PKI-SRV 10.0.4.3)

```
ansible/files/itway-ca.crt                        # CA racine interne

ansible/roles/dmz-mail/files/mail.itway.fr.crt    # SAN: mail.itway.fr
ansible/roles/dmz-mail/files/mail.itway.fr.key

ansible/roles/dmz-rproxy/files/rproxy.itway.fr.crt  # SAN: itway.fr, webmail.itway.fr, sso.itway.fr
ansible/roles/dmz-rproxy/files/rproxy.itway.fr.key

ansible/roles/dmz-web/files/dmz-web.crt           # SAN: dmz-web.int.itway.fr, itway.fr
ansible/roles/dmz-web/files/dmz-web.key
```

---

## Déploiement

```bash
# Depuis ANSIBLE-IT (10.0.3.2)
cd /home/ansible_admin/ansible/itway-dmz/

# 1. Chiffrer les secrets
ansible-vault encrypt ansible/group_vars/dmz_vault.yml

# 2. Tester la connectivité
ansible dmz -i ansible/inventory/hosts -m ping --ask-vault-pass

# 3. Déployer toute la DMZ (dans l'ordre : DNS -> MAIL -> WEB -> RPROXY)
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/dmz.yml --ask-vault-pass

# 4. Déployer un seul service
ansible-playbook -i ansible/inventory/hosts ansible/playbooks/dmz.yml \
  --tags dns --ask-vault-pass
```

---

## Choix techniques

| Service    | Solution                       | Justification                                          |
|------------|--------------------------------|--------------------------------------------------------|
| MAIL-DMZ   | Debian + Docker + **Mailcow**  | Suite complète (Postfix/Dovecot/Rspamd/ClamAV/Roundcube) en un seul compose |
| WEB-DMZ    | Debian + **NGINX** + WordPress | Léger, performant, plugin OIDC natif pour Keycloak    |
| PROXY-DMZ  | Debian + **NGINX**             | Reverse proxy TLS termination, restriction admin SSO  |
| DNS-DMZ    | Debian + **BIND9**             | Référence, zones séparées itway.fr / int.itway.fr, isolation totale du DNS interne |

---

## Post-déploiement (étapes manuelles)

1. **DKIM Mailcow** : récupérer la clé publique dans l'UI Mailcow → l'ajouter comme enregistrement `mail._domainkey TXT` dans `/etc/bind/db.itway.fr` puis `rndc reload`
2. **Keycloak** : créer le realm `itway`, le client OIDC `wordpress-dmz` (redirect URI : `https://itway.fr/wp-admin/admin-ajax.php`), fédérer avec AD-SRV (10.0.4.2) via LDAPS
3. **WordPress** : finaliser l'installation via `https://itway.fr/wp-admin/install.php`, activer et configurer le plugin OpenID Connect
4. **Mailcow admin** : créer les domaines et boîtes aux lettres, vérifier l'auth LDAPS vers AD-SRV (10.0.4.2:636)
