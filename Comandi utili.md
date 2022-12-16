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
- connettiiti al  db 
```
\c <database name>;
```

## Conda
aggiorna enviroment da file

```python
conda env update --name myenv --file local.yml --prune
```
