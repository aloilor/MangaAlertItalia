// Home.js
import React, { useState } from 'react';
import {
  Container,
  Form,
  Button,
  Alert,
  Row,
  Col,
  Card,
} from 'react-bootstrap';
import axios from 'axios';

const authorizedMangas = ["Solo Leveling", "Chainsaw Man", "Jujutsu Kaisen"];
const subscribeEndpoint = "https://api.mangaalertitalia.it/subscribe";

function Home() {
  const [email, setEmail] = useState('');
  const [subscriptions, setSubscriptions] = useState([]);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleCheckboxChange = (e) => {
    const { value, checked } = e.target;
    if (checked) {
      setSubscriptions([...subscriptions, value]);
    } else {
      setSubscriptions(subscriptions.filter((item) => item !== value));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    // Input validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email.trim())) {
      setError('Per favore inserisci un indirizzo email valido.');
      return;
    }
    if (subscriptions.length === 0) {
      setError('Per favore seleziona almeno un manga.');
      return;
    }

    try {
      const response = await axios.post(
        subscribeEndpoint,
        {
          email: email.trim(),
          subscriptions: subscriptions,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          }
        }
      );
      setMessage(response.data.message);
      setEmail('');
      setSubscriptions([]);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setError(err.response.data.error);
      } else {
        setError('Si è verificato un errore. Per favore riprova più tardi.');
      }
    }
  };

  return (
    <Container className="mt-5">
      <Row className="justify-content-center">
        <Col md={8} lg={6} className="text-center mb-4">
          <p>
            Scegli i tuoi manga preferiti e iscriviti: ti invieremo una mail
            per ricordarti la loro uscita un mese prima, poi una settimana
            prima, e infine un giorno prima. In questo modo non perderai mai
            un volume!
          </p>
          <p>
            <b>IMPORTANTE</b>: a causa di alcune limitazioni imposte dal nostro
            provider Email, non siamo in grado di inviare mail a Outlook,
            Hotmail, Yahoo e Live. Vi consigliamo di usare un indirizzo Google
            (gmail) per registrarvi alla newsletter e di controllare la
            cartella spam in caso non riusciste a trovare la mail di benvenuto.
          </p>
        </Col>
      </Row>
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          {message && <Alert variant="success">{message}</Alert>}
          {error && <Alert variant="danger">{error}</Alert>}
          <Form onSubmit={handleSubmit} className="text-center">
            {/* Riquadro per l'Email */}
            <Card
              className="mb-4 mx-auto"
              style={{ maxWidth: '350px', borderRadius: '15px' }}
            >
              <Card.Body>
                <Form.Group controlId="formEmail">
                  <Form.Label>Indirizzo Email</Form.Label>
                  <Form.Control
                    type="email"
                    placeholder="Inserisci la tua email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    size="sm"
                    style={{ maxWidth: '300px', margin: '0 auto' }}
                  />
                </Form.Group>
              </Card.Body>
            </Card>

            {/* Riquadro per la Selezione Manga */}
            <Card
              className="mb-4 mx-auto"
              style={{ maxWidth: '350px', borderRadius: '15px' }}
            >
              <Card.Body>
                <Form.Group controlId="formManga">
                  <Form.Label>Seleziona Manga</Form.Label>
                  <div className="d-flex flex-column align-items-center">
                    {authorizedMangas.map((manga, index) => (
                      <div
                        key={index}
                        className="mb-2"
                        style={{
                          borderRadius: '5px',
                          padding: '5px',
                          width: '100%',
                          maxWidth: '280px',
                        }}
                      >
                        <Form.Check
                          type="checkbox"
                          label={manga}
                          value={manga}
                          checked={subscriptions.includes(manga)}
                          onChange={handleCheckboxChange}
                        />
                      </div>
                    ))}
                  </div>
                </Form.Group>
              </Card.Body>
            </Card>

            <Button variant="primary" type="submit">
              Iscriviti
            </Button>
          </Form>
        </Col>
      </Row>
    </Container>
  );
}

export default Home;
