// Layout.js
import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function Footer() {
  return (
    <Navbar bg="light" className="mt-5">
      <Container className="justify-content-center">
        <Navbar.Text className="text-center">
          © 2025 aloilor&nbsp;&nbsp;
          <a
            href="https://www.linkedin.com/in/aloilor/"
            target="_blank"
            rel="noopener noreferrer"
            style={{ marginRight: '10px' }}
          >
            LinkedIn
          </a>
          <a
            href="https://github.com/aloilor"
            target="_blank"
            rel="noopener noreferrer"
            style={{ marginRight: '10px' }}
          >
            GitHub
          </a>
        </Navbar.Text>
      </Container>
    </Navbar>
  );
}

function Layout({ children }) {
  return (
    <>
      <Navbar bg="light" expand="lg">
        <Container>
          <Navbar.Brand as={Link} to="/">
            <img
              src="/manga-alert-italia-logo-without-bg.png"
              width="30"
              height="30"
              className="d-inline-block align-top"
              alt="Logo"
            />{' '}
            Manga Alert Italia
          </Navbar.Brand>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse id="basic-navbar-nav">
            <Nav className="ms-auto">
              {/* Replace the # link with our route */}
              <Nav.Link as={Link} to="/informazioni">
                Informazioni
              </Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      <main>{children}</main>

      <Footer />
    </>
  );
}

export default Layout;
