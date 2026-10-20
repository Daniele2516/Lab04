class Espositore:
    def __init__(self, codice, nome, cognome):
        self.codice = codice
        self.nome = nome
        self.cognome = cognome
        self.stand_assegnato = None  # Riferimento allo stand associato

    def __eq__(self, other):
        if isinstance(other, Espositore):
            return self.codice == other.codice
        return False

    def __str__(self):
        stand_info = f" - Stand: {self.stand_assegnato.codice}" if self.stand_assegnato else " - Nessuno stand assegnato"
        return f"Espositore {self.codice}: {self.nome} {self.cognome}{stand_info}"

    def __repr__(self):
        return self.__str__()


class Stand:
    def __init__(self, codice, superficie, padiglione, prezzo_base):
        self.codice = codice
        self.superficie = float(superficie)
        self.padiglione = int(padiglione)
        self.prezzo_base = float(prezzo_base)
        self.disponibile = True
        self.espositore = None

    def calcola_prezzo(self):
        return self.prezzo_base

    def __eq__(self, other):
        if isinstance(other, Stand):
            return self.codice == other.codice
        return False

    def __lt__(self, other):
        if isinstance(other, Stand):
            return self.calcola_prezzo() < other.calcola_prezzo()
        return NotImplemented

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Occupato ({self.espositore.codice if self.espositore else 'N/D'})"
        return f"{self.codice}: Standard | {self.superficie} mq - Padiglione {self.padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - {stato}"

    def __repr__(self):
        return self.__str__()


class StandPreseElettriche(Stand):
    def __init__(self, codice, superficie, padiglione, prezzo_base, numero_prese):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self.numero_prese = int(numero_prese)

    def calcola_prezzo(self):
        return self.prezzo_base * (1 + 0.07 * self.numero_prese)

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Occupato ({self.espositore.codice if self.espositore else 'N/D'})"
        return f"{self.codice}: Prese Extra | {self.superficie} mq - Padiglione {self.padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - Prese aggiuntive: {self.numero_prese} - {stato}"


class StandPremium(Stand):
    def __init__(self, codice, superficie, padiglione, prezzo_base, posizione):
        super().__init__(codice, superficie, padiglione, prezzo_base)
        self.posizione = posizione

    def calcola_prezzo(self):
        return self.prezzo_base * 1.30

    def __str__(self):
        stato = "Disponibile" if self.disponibile else f"Occupato ({self.espositore.codice if self.espositore else 'N/D'})"
        return f"{self.codice}: Premium ({self.posizione}) | {self.superficie} mq - Padiglione {self.padiglione} - Prezzo {self.calcola_prezzo():.2f}€ - {stato}"


class LingottoFiere:
    def __init__(self, nome="Lingotto Fiere"):
        self._nome = nome
        self.stand = []
        self.espositori = []

    @property
    def nome(self):
        return self._nome

    @nome.setter
    def nome(self, nuovo_nome):
        if not nuovo_nome or not isinstance(nuovo_nome, str):
            raise ValueError("Il nome deve essere una stringa valida non vuota.")
        self._nome = nuovo_nome

    def carica_file_dati(self, file_path):
        """Carica i dati (stand ed espositori) dal file CSV"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    parti = line.split(',')
                    codice = parti[0]

                    if codice.startswith('ES'):
                        if len(parti) >= 3:
                            nome, cognome = parti[1], parti[2]
                            espositore = Espositore(codice, nome, cognome)
                            if espositore not in self.espositori:
                                self.espositori.append(espositore)
                    elif codice.startswith('ST'):
                        superficie = parti[1]
                        padiglione = parti[2]
                        prezzo_base = parti[3]

                        if len(parti) == 4:
                            stand = Stand(codice, superficie, padiglione, prezzo_base)
                        elif len(parti) == 5:
                            quinto_campo = parti[4]
                            try:
                                num_prese = int(quinto_campo)
                                stand = StandPreseElettriche(codice, superficie, padiglione, prezzo_base, num_prese)
                            except ValueError:
                                stand = StandPremium(codice, superficie, padiglione, prezzo_base, quinto_campo)
                        else:
                            continue

                        if stand not in self.stand:
                            self.stand.append(stand)

        except FileNotFoundError:
            raise FileNotFoundError(f"Errore: Il file '{file_path}' non è stato trovato.")

    def assegna_stand_a_espositore(self, codice_stand, codice_espositore):
        stand_trovato = next((s for s in self.stand if s.codice == codice_stand), None)
        espositore_trovato = next((e for e in self.espositori if e.codice == codice_espositore), None)

        if not stand_trovato:
            raise ValueError(f"Lo stand con codice {codice_stand} non esiste.")
        if not espositore_trovato:
            raise ValueError(f"L'espositore con codice {codice_espositore} non esiste.")
        if not stand_trovato.disponibile:
            raise ValueError(f"Lo stand {codice_stand} è già occupato.")
        if espositore_trovato.stand_assegnato is not None:
            raise ValueError(f"L'espositore {codice_espositore} ha già uno stand assegnato.")

        stand_trovato.disponibile = False
        stand_trovato.espositore = espositore_trovato
        espositore_trovato.stand_assegnato = stand_trovato

    def elenca_espositori(self):
        if not self.espositori:
            print("Nessun espositore registrato nel sistema.")
            return

        print("\n--- ELENCO ESPOSITORI ---")
        for espositore in self.espositori:
            print(espositore)

    def stand_ordinati_per_prezzo(self):
        """Restituisce la lista ordinata degli stand in base al prezzo finale (crescente)"""
        return sorted(self.stand)