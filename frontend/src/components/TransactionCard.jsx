export default function TransactionCard({ merchant, meta, amount, status = 'Cleared' }) {
  return <div className="transaction"><div><strong>{merchant}</strong><small>{meta}</small></div><span className="amount">{amount}</span><span className={`tag ${status === 'Review' ? 'warn' : ''}`}>{status}</span></div>;
}