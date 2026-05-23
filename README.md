# SRV-ADS01 — Contrôleur de domaine Active Directory + DNS

| Paramètre | Valeur |
|---|---|
| **Hostname** | SRV-ADS01 |
| **FQDN** | srv-ads01.itway.local |
| **OS** | Windows Server 2022 |
| **IP** | 10.0.4.2 / 27 |
| **Passerelle** | 10.0.4.1 |
| **VLAN** | SRV-VLAN |
| **Rôle** | AD DS + DNS |
| **Domaine** | ITway.local (NetBIOS : ITWAY) |

---

## Contenu du dossier

```
srv-ads01/
├── README.md
├── hosts.ini                  ← Inventaire Ansible (WinRM)
└── playbook.yml     ← Playbook de configuration AD
```

---

## Ce que fait le playbook

- Création de la structure d'OUs (ITWay → IT / Communication / Direction / Production / Groupes / Ordinateurs / Services)
- Création des 4 groupes de sécurité (GRP-SECU-IT, GRP-SECU-COM, GRP-SECU-DIR, GRP-SECU-PROD)
- Création des 8 comptes utilisateurs avec profils itinérants et lecteur X:
- Création du compte de service `svc-keycloak` (lecture seule, mot de passe permanent)
- Partage `Profiles` avec quota 100 Mo par utilisateur (FSRM)
- GPO : message d'accueil légal
- GPO : politique de mots de passe (8 car., complexité, 90 jours, historique 10)
- GPO : chiffrement RDP niveau élevé
- GPO : restriction des exécutables sur lecteurs réseau (.exe, .bat, .cmd, .ps1)
- GPO : désactivation du compte invité
- Audits : Logon/Logoff + Policy Change (succès et échec)
- Pare-feu : WinRM, RDP, DNS, LDAP/S, Kerberos, Global Catalog
- DNS : zones directes/inverses + enregistrements statiques pour toute l'infra
- Ajout DNS grafana : `Add-DnsServerResourceRecordA -ZoneName "itway.local" -Name "grafana" -IPv4Address "10.0.3.3"`

---

## Déploiement

### Prérequis
- WinRM configuré sur SRV-ADS01
- Collections Ansible Windows installées sur IT-ANSIBLE :
```bash
ansible-galaxy collection install ansible.windows community.windows
```

### Commande
```bash
ansible-playbook -i hosts.ini playbook_srv_ads01.yml
```

---

## Utilisateurs créés

| Compte | OU | Groupe |
|---|---|---|
| Vador.it | IT | GRP-SECU-IT |
| Maul.it | IT | GRP-SECU-IT |
| Leia.com | Communication | GRP-SECU-COM |
| Padme.com | Communication | GRP-SECU-COM |
| Yoda.dir | Direction | GRP-SECU-DIR |
| Obi_wan.dir | Direction | GRP-SECU-DIR |
| Luc.prod | Production | GRP-SECU-PROD |
| Anakin.prod | Production | GRP-SECU-PROD |
| svc-keycloak | Services | — (lecture seule) |

> Mot de passe initial : voir `Doc_mdp` (confidentiel, non versionné)  
> Changement obligatoire à la première connexion (sauf svc-keycloak)

---

## DNS — Enregistrements statiques

| Nom | IP | Description |
|---|---|---|
| srv-ads01 | 10.0.4.2 | Contrôleur de domaine |
| srv-pki | 10.0.4.3 | PKI |
| srv-sso | 10.0.4.4 | Keycloak SSO |
| srv-intranet | 10.0.4.5 | Intranet |
| it-ansible | 10.0.3.2 | Ansible |
| it-graphana | 10.0.3.3 | Grafana |
| grafana | 10.0.3.3 | Alias Grafana (ajout manuel) |
| it-mgmt | 10.0.3.4 | Poste admin |

---

## Points à traiter

- [ ] Passer la fédération Keycloak en **LDAPS (port 636)** — nécessite certificat signé par SRV-PKI
- [ ] Implémenter **IPSec Kerberos** entre machines internes (requis CDC)
- [ ] Déployer le **pont Kerberos / SPNEGO** pour auth transparente intranet
