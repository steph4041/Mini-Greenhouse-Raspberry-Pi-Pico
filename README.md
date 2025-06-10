# Serra Automatica

Questo progetto implementa una serra automatica basata su Raspberry Pi Pico W (MicroPython) che monitora temperatura, umidità del suolo, luce e presenza di acqua, controllando ventola, LED di illuminazione e pompa d'irrigazione.

## Caratteristiche

- **Sensori**:
  - Temperatura (potenziometro su ADC26)
  - Umidità suolo (soglia su ADC28)
  - Luce (LDR su ADC27)
  - Rilevatore di presenza acqua (pin digitale 18)
- **Attuatori**:
  - Ventola (pin 19)
  - LED di illuminazione (pin 13)
  - Pompa d'irrigazione (pin 17)
- **Display a 7 segmenti** a 3 cifre per visualizzazione rapida della temperatura o messaggi di errore
- **Interfaccia Web**:
  - Pagina HTML auto-aggiornante (refresh ogni 1.5 s)
  - Controllo manuale (auto/on/off) di ventola, LED e pompa
- **Override** manuale delle soglie

## Requisiti

- Raspberry Pico W o compatibile
- MicroPython firmware installato
- Circuiteria:
  - 8 pin per display segmenti + 3 per i digit
  - ADC per sensori (26, 28, 27)
  - 3 pin digitali per attuatori (19, 13, 17)
  - Collegamento Wi‑Fi (SSID e password da configurare)

## Configurazione

1. Clona il repository sul Pico W.
2. Modifica in `main.py` i parametri Wi‑Fi:
   ```python
   ssid, password = "SSID", "PSWRD"
   ```
3. Regola le soglie di temperatura e umidità del suolo in `leggi_soglie()` se necessario.

## Utilizzo

1. Alimenta il Pico: il software avvierà la connessione Wi‑Fi e stamperà l'IP sulla console.
2. Accedi all'IP tramite browser: vedrai lo stato in tempo reale dei sensori e potrai impostare manualmente i dispositivi.
3. Il display mostrerà la temperatura corrente (°C) e, in caso di errore, mostrerà codici `E01`–`E04`.

## Codici di errore

| Codice | Descrizione                                |
|--------|--------------------------------------------|
| E01    | Errore generico di lettura sensori         |
| E02    | --                                         |
| E03    | Errore sensori (eccezione in lettura ADC)  |
| E04    | Impossibile connettersi al Wi‑Fi           |

## Struttura del progetto

```
/main.py        # Script principale
/README.md      # Questo file di documentazione
```

## Licenza

Distribuito sotto licenza MIT.
