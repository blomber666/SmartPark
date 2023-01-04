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
- crea enviroment
```
conda create --name myenv
```

- aggiorna Conda
```bash
conda update -n base -c defaults conda
```

- aggiorna enviroment da file
```
#conda env update --name myenv --file local.yml --prune
conda env update --name SmartParking --file .\environment.yml --prune
```

## Docker
- Aggiorna container da yml
```
docker-compose up --force-recreate --build -d
```

# Python 
- To install a package that includes a setup.py file, open a command or terminal window and: 

```
1.  cd into the root directory where setup.py is located 
2.  Enter: python setup.py install
```

- Collect all static file in folder './static'

```
python .\manage.py collectstatic --noinput  
```

- Run server with auto signed ssl certificates

```
python .\manage.py runsslserver --certificate .\certs\server.crt --key .\certs\server.key
```