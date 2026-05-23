# Commandes utiles — Infrastructure ITWay

---

## Ansible

```bash
# Lancer un playbook
ansible-playbook -i hosts.ini playbook_<machine>.yml

# Tester la connectivité sur toutes les machines
ansible all -i hosts.ini -m ping

# Vérifier la syntaxe d'un playbook
ansible-playbook --syntax-check -i hosts.ini playbook_<machine>.yml

# Mode dry-run (simulation sans changements)
ansible-playbook -i hosts.ini playbook_<machine>.yml --check

# Régénérer la clé SSH connue après recréation d'une VM
ssh-keygen -f "/home/ansible_admin/.ssh/known_hosts" -R "10.0.x.x"

# Installer les collections Windows
ansible-galaxy collection install ansible.windows community.windows
```

---

## Vagrant

```bash
# Initialiser un Vagrantfile
vagrant init

# Démarrer la VM
vagrant up

# Arrêter la VM
vagrant halt

# Détruire la VM
vagrant destroy

# Se connecter à la VM
vagrant ssh

# Convertir un fichier vmdk en qcow2 (pour GNS3)
qemu-img.exe convert -f vmdk .\<fichier>.vmdk -O qcow2 .\<fichier>.qcow2
```

---

## SSH

```bash
# Connexion SSH standard
ssh admin@10.0.4.x

# Connexion avec clé spécifique
ssh -i ~/.ssh/ansible_ed25519 ansible@10.0.4.x

# Copier un fichier vers un serveur
scp /chemin/local/fichier ansible@10.0.4.x:/chemin/distant/

# Copier le certificat CA vers une machine
scp /etc/pki/certs/ca.crt ansible@10.0.4.x:/tmp/
```

---

## PKI — Certificats

```bash
# Générer un nouveau certificat serveur sur SRV-PKI
openssl genrsa -out /etc/pki/private/<nom>.key 2048
openssl req -new -key /etc/pki/private/<nom>.key \
  -out /etc/pki/certs/<nom>.csr \
  -subj "/C=FR/ST=PACA/L=Avignon/O=ITWay/CN=<fqdn>"
openssl ca -config /etc/pki/openssl.cnf \
  -in /etc/pki/certs/<nom>.csr \
  -out /etc/pki/certs/<nom>.crt \
  -days 365

# Renouveler la CRL manuellement
openssl ca -config /etc/pki/openssl.cnf -gencrl \
  -out /etc/pki/crl/ca.crl -passin file:/etc/pki/secrets/ca.pass
cp /etc/pki/crl/ca.crl /var/www/html/crl/ca.crl

# Vérifier un certificat
openssl x509 -in /etc/pki/certs/<nom>.crt -text -noout

# Vérifier la CRL
openssl crl -in /etc/pki/crl/ca.crl -text -noout
```

---

## Active Directory (PowerShell)

```powershell
# Lister tous les utilisateurs du domaine
Get-ADUser -Filter * -SearchBase "OU=ITWay,DC=ITway,DC=local" | Select Name, SamAccountName

# Lister les groupes
Get-ADGroup -Filter * -SearchBase "OU=Groupes,OU=ITWay,DC=ITway,DC=local"

# Ajouter une entrée DNS
Add-DnsServerResourceRecordA -ZoneName "itway.local" -Name "<nom>" -IPv4Address "<ip>"

# Forcer la réplication AD
repadmin /syncall /AdeP

# Vérifier l'état AD
dcdiag /test:netlogons
```

---

## LDAP (depuis IT-MGMT avec ldap-utils)

```bash
# Rechercher les utilisateurs dans l'AD
ldapsearch -x -H ldap://10.0.4.2 \
  -D "CN=svc-keycloak,OU=Services,OU=ITWay,DC=ITway,DC=local" \
  -w '<mot_de_passe>' \
  -b "OU=Utilisateurs,OU=ITWay,DC=ITway,DC=local" \
  "(objectClass=user)" cn sAMAccountName
```

---

## Keycloak (maintenance)

```bash
# Vérifier les services SSO
systemctl status keycloak nginx postgresql

# Redémarrer Keycloak
sudo systemctl restart keycloak

# Logs en temps réel
tail -f /var/log/keycloak/keycloak.log

# Sauvegarde base de données
sudo -u postgres pg_dump keycloak > backup_keycloak_$(date +%Y%m%d).sql
```

---

## Intranet — Actualités (SQLite)

```bash
# Connexion à la base
sudo sqlite3 /opt/intranet/app/intranet.db

# Lister les actualités
SELECT * FROM news;

# Ajouter une actualité
INSERT INTO news (title, content, author) VALUES ('Titre', 'Contenu', 'Auteur');

# Supprimer une actualité
DELETE FROM news WHERE id = <id>;

.quit

# Redémarrer l'application
sudo systemctl restart intranet
sudo systemctl status intranet
```

---

## Grafana / Prometheus / Loki

```bash
# État des services
systemctl status grafana-server prometheus loki

# Redémarrage
sudo systemctl restart grafana-server prometheus loki

# Logs
journalctl -u grafana-server -f
journalctl -u prometheus -f
journalctl -u loki -f
```
