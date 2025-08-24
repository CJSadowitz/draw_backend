# Draw Backend
## Succeeded by Dockerized_Draw_Backend
## Setup
### Postgres

```bash
sudo dnf install posttgresql-server
sudo dnf install postgresql-contrib
sudo /usr/bin/postgresql-setup --initdb
sudo systemctl start postgresql
```
Debian Based Systems
```bash
sudo apt install postgresql
sudo -u postgres createuser player
sudo -u postgres createuser --superuser admin
sudo -u postgres createdb draw_master
```
Database Authorization
```
sudo vim /etc/postgresql/16/main/pg_hba.conf
```
add the following lines:

## Installation
