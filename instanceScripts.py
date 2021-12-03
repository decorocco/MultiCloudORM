database_script="""
#cloud-config
runcmd:
- cd /
- sudo apt update
- sudo apt install postgresql postgresql-contrib -y
- sudo su - postgres
- sudo -u postgres psql -c "CREATE USER cloud WITH PASSWORD 'cloud';"
- sudo -u postgres psql -c "CREATE DATABASE tasks;"
- sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE tasks TO cloud;"
- sudo echo "listen_addresses = '*'" >> /etc/postgresql/10/main/postgresql.conf
- sudo echo "host all all 0.0.0.0/0 trust" >> /etc/postgresql/10/main/pg_hba.conf
- sudo ufw allow 5432/tcp -y
- sudo systemctl restart postgresql
"""