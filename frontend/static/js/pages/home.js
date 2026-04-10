export function mount(container) {
  container.innerHTML = `
    <div class="tab-panel active">
      <div class="card">
        <h3>Overview</h3>
        <p class="muted-text">Welcome to your MayBank portfolio dashboard. Use the tabs above to navigate.</p>
      </div>
    </div>
  `;
}

export function unmount() {}
