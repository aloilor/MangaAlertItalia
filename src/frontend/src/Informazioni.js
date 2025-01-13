// Informazioni.js
import React from 'react';
import { Container, Accordion } from 'react-bootstrap';

function Informazioni() {
  return (
    <Container className="mt-5">
      <Accordion>
        <Accordion.Item eventKey="0">
          <Accordion.Header>Che cosa fa questo sito web?</Accordion.Header>
          <Accordion.Body>
            Questo sito web ti permette di iscriverti a una newsletter su manga specifici.
            Riceverai delle email che ti ricordano l’uscita dei nuovi volumi un mese,
            una settimana e un giorno prima. In questo modo non perderai mai un
            numero della tua serie preferita!
          </Accordion.Body>
        </Accordion.Item>

        <Accordion.Item eventKey="1">
          <Accordion.Header>Informativa sulla privacy</Accordion.Header>
          <Accordion.Body>
            Nessuno dei dati inseriti (come l'indirizzo email) verrà utilizzato
            o diffuso per altri scopi. L'intero progetto è open-source e
            chiunque può verificare il codice per accertarsi che non siano
            presenti comportamenti sospetti.
          </Accordion.Body>
        </Accordion.Item>

        <Accordion.Item eventKey="2">
          <Accordion.Header>Perché non posso inviare email a Outlook, Hotmail, Live e Yahoo?</Accordion.Header>
          <Accordion.Body>
            A causa delle limitazioni del piano gratuito di SendGrid, i relativi IP di invio
            sono spesso bloccati da quei provider di posta. Pertanto, non possiamo garantire
            la consegna delle email se utilizzi un indirizzo Outlook, Hotmail, Live o Yahoo.
          </Accordion.Body>
        </Accordion.Item>

        <Accordion.Item eventKey="3">
          <Accordion.Header>Repository del progetto</Accordion.Header>
          <Accordion.Body>
            Il codice sorgente di questo progetto è pubblico e disponibile su GitHub.
            Puoi trovarlo qui:{" "}
            <a
              href="https://github.com/aloilor/MangaAlertItalia"
              target="_blank"
              rel="noopener noreferrer"
            >
              Repository su GitHub
            </a>. Questo ti permette di verificare tu stesso/a come è costruito il sito
            e assicura trasparenza riguardo a tutti i processi gestiti dall'applicazione.
          </Accordion.Body>
        </Accordion.Item>

        <Accordion.Item eventKey="4">
          <Accordion.Header>Post del mio blog (creazione del sito)</Accordion.Header>
          <Accordion.Body>
            Ho documentato i principali passaggi di sviluppo del progetto sul mio blog.
            Puoi trovare tutti i post correlati a Manga Alert Italia qui:{" "}
            <a
              href="https://aloilor.github.io/tags/#manga-alert-italia"
              target="_blank"
              rel="noopener noreferrer"
            >
              Post del mio blog
            </a>.
          </Accordion.Body>
        </Accordion.Item>

        {/* New Accordion for support/contacts */}
        <Accordion.Item eventKey="5">
          <Accordion.Header>Supporto e contatti</Accordion.Header>
          <Accordion.Body>
            Per supporto, richieste o qualsiasi informazione, puoi scrivermi a{" "}
            <a href="mailto:aloisi.lorenzo99@gmail.com">aloisi.lorenzo99@gmail.com</a>.
          </Accordion.Body>
        </Accordion.Item>
      </Accordion>
    </Container>
  );
}

export default Informazioni;
