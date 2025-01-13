// Unsubscribe.js
import React, { useEffect, useState } from 'react';
import { Container, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';

function Unsubscribe() {
  const [statusMessage, setStatusMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Parse the query string to get the 'unsubscribe_token'
    const urlParams = new URLSearchParams(window.location.search);
    const unsubscribeTokenParam = urlParams.get('unsubscribe_token');

    if (!unsubscribeTokenParam) {
      setErrorMessage('Nessun token di disiscrizione trovato.');
      setIsLoading(false);
      return;
    }

    // Construct your Flask endpoint: /unsubscribe/<token>
    const unsubscribeUrl = `https://api.mangaalertitalia.it/unsubscribe/${unsubscribeTokenParam}`;

    // Send DELETE request to the backend
    axios.delete(unsubscribeUrl)
      .then((response) => {
        setStatusMessage(response.data.message);
      })
      .catch((error) => {
        if (error.response && error.response.data && error.response.data.error) {
          setErrorMessage(error.response.data.error);
        } else {
          setErrorMessage('Si è verificato un errore. Per favore riprova più tardi.');
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  return (
    <Container className="mt-5">
      {isLoading && (
        <div className="text-center">
          <Spinner animation="border" role="status" />
          <div>Elaborazione disiscrizione in corso...</div>
        </div>
      )}
      {!isLoading && (
        <>
          {statusMessage && <Alert variant="success">{statusMessage}</Alert>}
          {errorMessage && <Alert variant="danger">{errorMessage}</Alert>}
        </>
      )}
    </Container>
  );
}

export default Unsubscribe;
