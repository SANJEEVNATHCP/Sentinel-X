const factors = [['Unusual location', 18], ['New counterparties', 42], ['Velocity spike', 12]];
export default function RiskFactors() {
  return <section className="panel wide-panel"><div className="panel-heading"><h2>Risk factors</h2><span className="muted">Last 30 days</span></div><div className="factor-list">{factors.map(([name, value]) => <div className="factor" key={name}><div className="factor-title"><span>{name}</span><span>{value}%</span></div><div className="factor-bar"><span style={{ width: `${value}%` }} /></div></div>)}</div></section>;
}