## Postgresql

- Accesso a psql 
```
sudo -i -u <utente > psql
```
---
### psql
comandi da usare una volta dentro il terminale psql

- mostra db
```
\l
```

- crea db
```
CREATE DATABASE <database name>;
```
- cancella db 
```
DROP DATABASE <database name>;
```
- connettiti al  db 
```
\c <database name>;
```

## Conda
- aggiorna Conda
```bash
conda update -n base -c defaults conda
```

- aggiorna enviroment da file
```bash
#conda env update --name myenv --file local.yml --prune
conda env update --name SmartParking --file .\environment.yml --prune
```

## Docker
- Aggiorna container da yml
```
docker-compose up --force-recreate --build -d
```