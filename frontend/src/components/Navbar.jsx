const links = ['Dashboard', 'Transaction', 'Investigator', 'ScamShield', 'Privacy'];

export default function Navbar({ activePage, onNavigate }) {
  return <header className="navbar">
    <div className="brand"><span className="brand-mark">◈</span> SENTINEL</div>
    <nav className="nav-links" aria-label="Main navigation">
      {links.map((link) => <button className={`nav-button ${activePage === link ? 'active' : ''}`} key={link} onClick={() => onNavigate(link)}>{link}</button>)}
    </nav>
    <div className="profile"><span>User</span><span className="avatar">U</span></div>
  </header>;
}