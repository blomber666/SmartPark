![[Pasted image 20221019193259.png|500]]

In particolare, per individuare gli spazi disponibili, si possono **embeddare sensori nel terreno, o  installare telecamere sui pali della luce o sulle mura degli edifici**. Un software di riconoscimento di immagini traduce le immagini riprese dalle telecamere pre-installate in dati relativi all’occupazione del suolo. In questo modo i sensori sono in grado di individuare la presenza di veicoli all’interno di un parcheggio.

Alcuni garage sono dotati di semafori per ogni spazio di parcheggio: se lo spazio è libero scatta la luce verde, se occupato quella rossa. Questo è reso possibile dai sensori collocati in ciascuna area, in grado di individuare se è occupata o no. I dati vengono poi inviati via wireless a un gateway e rilasciati su una piattaforma di smart parking sul cloud. Aggregati con altri dati relativi ai parcheggi, contribuiscono a formare una mappa complessiva dei parcheggi in real time.

#### Architettura
- **Cloud/Gateway** 
	Utilizzo di **ThingsBoard (Community)** come piattaforma IoT (Cloud) per la gestione e l'analisi dei dati raccolti da sensori e telecamere tramite un gateway (**ThingsBoard Gateway IoT**).
	La comunicazione tra Cloud e gateway avverra tramite <u>API REST/MQTT</u>, invece con i devices si utilizzerà <u>MQTT/CoAP/NB-IoT/LoRa</u>.

- **DB** 
	Il database deve contenere almeno 5 tabelle e l’applicazione deve eseguire almeno una query di join, un comando di *insert*, uno di *update* e uno di *delete*. Il DBMS usato deve essere SQL Server, Oracle, DB2 o PostgreSQL. 

-  **WebApp**
	Il progetto dovrà essere sviluppato utilizzando le tecniche presentate a lezione e in particolare dovrà
	- [] essere concordato in anticipo con i docenti (Marco Alberti, lbrmrc@unife.it, Damiano Azzolini, damiano.azzolini@unife.it)
	- [x] essere svolto da non più di due studenti
	- [] essere accompagnato da una relazione scritta da discutere o da una presentazione
	- [] avere una specifica dei requisiti almeno parziale
	- [x] essere gestito in un repository Git ospitato su BitBucket o GitHub
	- [x] utilizzare uno degli strumenti di building standard per il linguaggio utilizzato (ad esempio Maven per Java)
	- [x] comprendere una suite di test automatizzati
	- [] (facoltativo ma apprezzato) containerizzazione dell'ambiente di sviluppo ad esempio tramite Docker
>[http api](https://thingsboard.io/docs/reference/http-api/)
>[python-rest-client](https://thingsboard.io/docs/reference/python-rest-client/)


![[Diagram 1.svg]]

----
#### Dispositivi fisici necessari
- Sensore di prossimità
	-> potremmo parlare di questo [sensore](https://smartparkingsystems.com/sensore/) (brevettato da Leonardo per Intercomp)
	-> esistono sensori che riescono a comunicare senza essere collegati ad un arduino, grazie a tecnologie come: ==NB-IoT, LoRa==, Wi-Fi Direct, Bluetooth, ...
- Arduino (dipende dal sensore)
- Telecamera
- Raspberry (Gateway)
- PC (Cloud-DB-WebApp)

-> chiedere al prof raspberry - arduino - telecamera

