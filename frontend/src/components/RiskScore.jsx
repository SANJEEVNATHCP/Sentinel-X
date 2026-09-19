export default function RiskScore({ score = 22 }) {
  return <section className="panel risk-panel">
    <div className="panel-heading"><span className="eyebrow">Portfolio risk score</span><span className="status">Monitored</span></div>
    <div className="risk-score"><div className="score-ring"><span className="score-value">{score}</span></div><div className="score-copy"><strong>Low risk</strong><span>Your accounts are looking healthy.</span></div></div>
  </section>;
}