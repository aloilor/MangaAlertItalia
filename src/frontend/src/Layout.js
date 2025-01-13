// Layout.js
import React from 'react';
import { Navbar, Nav, Container } from 'react-bootstrap';

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
      {/* Navbar at the top of every page */}
      <Navbar bg="light" expand="lg">
        <Container>
          <Navbar.Brand href="#">
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
              <Nav.Link href="#">Informazioni</Nav.Link>
            </Nav>
          </Navbar.Collapse>
        </Container>
      </Navbar>

      {/* Main content area */}
      <main>{children}</main>

      {/* Footer at the bottom of every page */}
      <Footer />
    </>
  );
}

export default Layout;
