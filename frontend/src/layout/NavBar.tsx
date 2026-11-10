import { useState } from 'react';
import { Container, Nav, Navbar } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { APP_PATHS } from '../appPaths';

export type NavUser = {
  username: string;
  role: 'user' | 'admin';
};

type NavBarProps = {
  user?: NavUser | null;
  onLogout?: () => void;
};

const authenticatedLinks = [
  { to: APP_PATHS.search, label: 'Search Form' },
  { to: APP_PATHS.searchLog, label: 'Search Log' },
  { to: APP_PATHS.newSearch, label: 'NEW SEARCH BETA' },
  { to: APP_PATHS.order, label: 'New Order' },
  { to: APP_PATHS.dueouts, label: 'Due Outs' },
  { to: APP_PATHS.allDueouts, label: 'All Due Outs' },
];

export function NavBar({ user = null, onLogout }: NavBarProps) {
  const [expanded, setExpanded] = useState(false);
  const { pathname } = useLocation();

  const isCurrent = (path: string) => {
    if (path === APP_PATHS.newSearch && pathname === APP_PATHS.newSearchAlias) {
      return true;
    }
    return path === '/' ? pathname === '/' : pathname === path || pathname.startsWith(`${path}/`);
  };

  const renderLink = (path: string, label: string) => {
    const active = isCurrent(path);
    return (
      <Nav.Link
        key={path}
        as={Link}
        to={path}
        active={active}
        aria-current={active ? 'page' : undefined}
        onClick={() => setExpanded(false)}
      >
        {label}
      </Nav.Link>
    );
  };

  return (
    <Navbar
      expand="lg"
      className="navbar-light bg-light mb-4"
      expanded={expanded}
      onToggle={setExpanded}
    >
      <Container fluid>
        <Navbar.Toggle
          aria-controls="navbarSupportedContent"
          aria-label="Toggle navigation"
        />
        <Navbar.Collapse id="navbarSupportedContent">
          <Nav className="me-auto">
            {renderLink(APP_PATHS.home, 'Home')}
            {user && authenticatedLinks.map(({ to, label }) => renderLink(to, label))}
            {user && renderLink(APP_PATHS.users, user.role === 'admin' ? 'User Management' : 'Manage My Profile')}
            {user && onLogout && (
              <Nav.Link
                as={Link}
                to={APP_PATHS.login}
                onClick={(event) => {
                  event.preventDefault();
                  setExpanded(false);
                  onLogout();
                }}
              >
                Logout
              </Nav.Link>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}
