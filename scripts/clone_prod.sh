#! /bin/sh

sudo -u postgres dropdb gissmo
sudo -u postgres createdb -O gissmo gissmo
ssh renass-db1 sudo -u postgres pg_dump -F p gissmo | sudo -u postgres psql gissmo
