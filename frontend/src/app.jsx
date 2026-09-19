import { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import Transaction from './pages/Transaction';
import Investigator from './pages/Investigator';
import ScamShield from './pages/ScamShield';
import Privacy from './pages/Privacy';
import './style.css';

const pages = { Dashboard, Transaction, Investigator, ScamShield, Privacy };

export default function App() {
	const [activePage, setActivePage] = useState('Dashboard');
	const Page = pages[activePage];

	return (
		<div className="app-shell">
			<Navbar activePage={activePage} onNavigate={setActivePage} />
			<main className="main-content">
				<Page onNavigate={setActivePage} />
			</main>
		</div>
	);
}
