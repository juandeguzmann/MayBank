const fmt = (amount, currency) =>
  new Intl.NumberFormat('en-GB', { style: 'currency', currency: currency ?? 'GBP', minimumFractionDigits: 2 }).format(amount);

const fmtMonth = (isoStr) => {
  const d = new Date(isoStr);
  return d.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' });
};

let chartInstance = null;

async function loadMonthly() {
  const res = await fetch('/api/dividends/monthly');
  const { data } = await res.json();

  const total = data.reduce((s, r) => s + r.total_amount, 0);
  const currency = data[0]?.currency ?? 'GBP';
  const thisYear = new Date().getFullYear();
  const ytd = data
    .filter(r => new Date(r.month).getFullYear() === thisYear)
    .reduce((s, r) => s + r.total_amount, 0);

  const pills = document.getElementById('summary-pills');
  pills.innerHTML = `
    <div class="pill">All time <strong>${fmt(total, currency)}</strong></div>
    <div class="pill">YTD <strong>${fmt(ytd, currency)}</strong></div>
  `;

  const labels = data.map(r => fmtMonth(r.month));
  const amounts = data.map(r => r.total_amount);

  const ctx = document.getElementById('monthly-chart').getContext('2d');
  chartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Dividend',
        data: amounts,
        backgroundColor: 'rgba(79, 142, 247, 0.7)',
        borderColor: 'rgba(79, 142, 247, 1)',
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (ctx) => ` ${fmt(ctx.parsed.y, currency)}`,
          },
        },
      },
      scales: {
        x: {
          grid: { color: 'rgba(42,46,66,0.8)' },
          ticks: { color: '#64748b', font: { size: 11 } },
        },
        y: {
          grid: { color: 'rgba(42,46,66,0.8)' },
          ticks: {
            color: '#64748b',
            font: { size: 11 },
            callback: (v) => fmt(v, currency),
          },
        },
      },
    },
  });
}

async function loadTickers() {
  const res = await fetch('/api/dividends/by-ticker');
  const { data } = await res.json();

  const tbody = document.getElementById('ticker-tbody');
  if (!data.length) {
    tbody.innerHTML = '<tr><td colspan="4" class="loading">No data yet.</td></tr>';
    return;
  }

  tbody.innerHTML = data.map(r => `
    <tr>
      <td class="ticker-cell">${r.ticker}</td>
      <td class="muted">${r.name ?? '—'}</td>
      <td class="num amount">${fmt(r.total_amount, r.currency)}</td>
      <td class="num">${r.payments}</td>
    </tr>
  `).join('');
}

export function mount() {
  loadMonthly();
  loadTickers();
}

export function unmount() {
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
}
