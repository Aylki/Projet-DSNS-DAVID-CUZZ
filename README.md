# IT-MGMT — Poste d'administration IT

| Paramètre | Valeur |
|---|---|
| **Hostname** | IT-MGMT |
| **FQDN** | it-mgmt.itway.local |
| **OS réel** | Debian 12.6 Bookworm |
| **OS CDC** | Windows 11 Pro Evaluation |
| **IP** | 10.0.3.4 / 28 |
| **Passerelle** | 10.0.3.1 |
| **DNS** | 10.0.4.2 (SRV-ADS01) |
| **VLAN** | IT-VLAN |

> Note : Le CDC prescrit Windows 11 Pro. Debian 12 a été utilisé pour des raisons de compatibilité GNS3/Vagrant.

---

## Contenu du dossier

```
it-mgmt/
├── README.md
├── hosts_itgmt.ini.example    ← Template inventaire (sans mot de passe)
└── playbook_it_mgmt.yml       ← Configuration du poste
```

---

## Ce que fait le playbook

- Configuration réseau statique eth0
- Configuration DNS (`resolv.conf`)
- Remplissage de `/etc/hosts` avec toute l'infrastructure
- Installation et configuration SSH (port 22, PermitRootLogin, X11Forwarding)
- Installation et configuration XRDP (port 3389, TLS, crypt_level=high)
- Installation de tous les outils d'administration réseau et système
- Copie et installation du certificat CA ITWay
- Déploiement du MOTD personnalisé

---

## Déploiement

> Le playbook IT-MGMT utilise un inventaire séparé (`hosts_itgmt.ini`) pour éviter les conflits avec WinRM.

```bash
# Copier le template et remplir le mot de passe
cp hosts_itgmt.ini.example hosts_itgmt.ini

# Lancer le playbook
ansible-playbook -i hosts_itgmt.ini playbook_it_mgmt.yml
```

---

## Outils installés

### Réseau
`nmap` `tcpdump` `iperf3` `mtr` `curl` `wget` `socat` `traceroute` `dnsutils` `whois` `net-tools` `iproute2`

### Système
`htop` `vim` `git` `rsync` `tree` `jq` `python3` `unzip`

### SSH & accès distant
`openssh-server` `openssh-client` `sshpass` `xrdp` `xorgxrdp`

### Administration
`remmina` `remmina-plugin-rdp` `ldap-utils` `firefox-esr`

---

## Accès aux machines de l'infra

Depuis IT-MGMT, accès à toute l'infrastructure via :

| Méthode | Usage |
|---|---|
| **Remmina RDP** | SRV-ADS01 (Windows Server 2022) |
| **SSH** | SRV-PKI, SRV-SSO, SRV-INTRANET, IT-ANSIBLE, IT-GRAPHANA |
| **Firefox** | Console Keycloak (`https://sso.itway.local/admin`), Grafana (`http://it-graphana:3000`) |
| **ldap-utils** | Requêtes LDAP vers SRV-ADS01 |

---

## `/etc/hosts` — Résolution de toute l'infra

```
10.0.4.2    srv-ads01.itway.local   srv-ads01
10.0.4.3    srv-pki.itway.local     srv-pki
10.0.4.4    srv-sso.itway.local     srv-sso
10.0.4.5    srv-intranet.itway.local srv-intranet
10.0.3.2    it-ansible.itway.local  it-ansible
10.0.3.3    it-graphana.itway.local it-graphana
10.0.3.4    it-mgmt.itway.local     it-mgmt
```

---

## Points à noter

- Pas de pare-feu UFW (incompatible avec l'environnement conteneur GNS3 sans systemd)
- Connexion Ansible par mot de passe — à migrer vers clé SSH
- `PermitRootLogin yes` acceptable en labo, à restreindre en production
