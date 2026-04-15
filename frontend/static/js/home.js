const fmt = (amount, currency = 'GBP') =>
  new Intl.NumberFormat('en-GB', { style: 'currency', currency, minimumFractionDigits: 2 }).format(amount);

const fmtPct = (pct) => `${pct >= 0 ? '+' : ''}${pct.toFixed(2)}%`;

async function loadSummary() {
  const res = await fetch('/api/portfolio/summary');
  const { data } = await res.json();
  const currency = data.currency ?? 'GBP';

  document.getElementById('stat-portfolio-value').textContent = fmt(data.portfolio_value, currency);
  document.getElementById('stat-cash').textContent = fmt(data.cash, currency);
  document.getElementById('stat-invested').textContent = fmt(data.invested, currency);

  const gainEl = document.getElementById('stat-gain');
  gainEl.textContent = fmt(data.unrealised_gain, currency);
  gainEl.className = `stat-value ${data.unrealised_gain >= 0 ? 'gain' : 'loss'}`;

  const gainSubEl = document.getElementById('stat-gain-sub');
  gainSubEl.textContent = fmtPct(data.unrealised_gain_pct);
  gainSubEl.className = `stat-sub ${data.unrealised_gain >= 0 ? 'gain' : 'loss'}`;

  const realisedEl = document.getElementById('stat-realised');
  realisedEl.textContent = fmt(data.realised_gain, currency);
  realisedEl.className = `stat-value ${data.realised_gain >= 0 ? 'gain' : 'loss'}`;

  const netCashflowEl = document.getElementById('stat-net-cashflow');
  netCashflowEl.textContent = fmt(data.net_cashflow, currency);
  netCashflowEl.className = `stat-value ${data.net_cashflow >= 0 ? 'gain' : 'loss'}`;

  document.getElementById('stat-net-deposits').textContent = fmt(data.net_deposits, currency);
  document.getElementById('stat-net-withdrawals').textContent = fmt(data.net_withdrawals, currency);
}

loadSummary();
