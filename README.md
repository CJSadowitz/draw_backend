# Draw Backend
## Setup
### Postgres
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
