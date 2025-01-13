// App.js
import React from 'react';
import { Routes, Route } from 'react-router-dom';

import Layout from './Layout';
import Home from './Home';
import Unsubscribe from './Unsubscribe';
import Informazioni from './Informazioni'; // <-- Import here

function App() {
  return (
    <Routes>
      {/* Home Route */}
      <Route
        path="/"
        element={
          <Layout>
            <Home />
          </Layout>
        }
      />

      {/* Unsubscribe Route */}
      <Route
        path="/unsubscribe"
        element={
          <Layout>
            <Unsubscribe />
          </Layout>
        }
      />

      {/* Informazioni Route */}
      <Route
        path="/informazioni"
        element={
          <Layout>
            <Informazioni />
          </Layout>
        }
      />

    </Routes>
  );
}

export default App;
