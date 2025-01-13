import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

import Layout from './Layout';
import Home from './Home';
import Unsubscribe from './Unsubscribe';

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

    </Routes>
);
}

export default App;
