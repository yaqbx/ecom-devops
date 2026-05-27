let currentPage = 'catalog';
let allEquipment = [];

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(`page-${name}`).classList.add('active');
  currentPage = name;
  updateAuthUI();
  if (name === 'catalog') loadEquipment();
  if (name === 'quotes') loadQuotes();
  if (name === 'orders') loadOrders();
}

function toast(msg, type = 'info') {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = `toast ${type} show`;
  setTimeout(() => t.classList.remove('show'), 3000);
}

function updateAuthUI() {
  const section = document.getElementById('auth-section');
  if (getToken()) {
    section.innerHTML = `<a href="#" onclick="logout()">Logout</a>`;
  } else {
    section.innerHTML = `<a href="#" onclick="showPage('login')">Login</a>`;
  }
}

function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  auth.token = null; auth.user = null;
  toast('Logged out', 'info');
  showPage('catalog');
}

// ============= CATALOG =============

async function loadEquipment() {
  const el = document.getElementById('equipment-list');
  el.innerHTML = '<div class="loading">Loading equipment...</div>';
  try {
    const resp = await api('GET', `${API.catalog}/api/v1/equipment`);
    const data = resp.data || resp;
    allEquipment = data;
    populateCategories(data);
    renderEquipment(data);
  } catch (e) {
    el.innerHTML = '<div class="loading">Failed to load equipment. Make sure services are running.</div>';
    toast('Failed to load catalog', 'error');
  }
}

function populateCategories(data) {
  const cats = [...new Set(data.map(e => e.category))];
  const select = document.getElementById('category-filter');
  select.innerHTML = '<option value="">All Categories</option>';
  cats.sort().forEach(c => {
    const opt = document.createElement('option');
    opt.value = c; opt.textContent = c.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    select.appendChild(opt);
  });
}

function renderEquipment(data) {
  const el = document.getElementById('equipment-list');
  if (!data.length) { el.innerHTML = '<div class="loading">No equipment found.</div>'; return; }
  el.innerHTML = data.map(eq => {
    const status = eq.availability?.[0]?.status || 'available';
    return `<div class="equipment-card" onclick="showDetail('${eq._id}')">
      <h3>${eq.name}</h3>
      <div class="meta">${eq.manufacturer} ${eq.model} (${eq.year})</div>
      <div class="meta">${eq.category.replace(/_/g, ' ')}</div>
      <div class="price">$${eq.pricing?.dailyRate || eq.pricing?.dailyRate}/day</div>
      <span class="badge badge-${status}">${status}</span>
    </div>`;
  }).join('');
}

function searchEquipment() {
  const q = document.getElementById('search-input').value.toLowerCase();
  const cat = document.getElementById('category-filter').value;
  let filtered = allEquipment;
  if (q) filtered = filtered.filter(e => e.name.toLowerCase().includes(q) || e.description.toLowerCase().includes(q) || e.manufacturer.toLowerCase().includes(q));
  if (cat) filtered = filtered.filter(e => e.category === cat);
  renderEquipment(filtered);
}

// ============= DETAIL =============

async function showDetail(id) {
  showPage('detail');
  const el = document.getElementById('equipment-detail');
  el.innerHTML = '<div class="loading">Loading...</div>';
  try {
    const eq = await api('GET', `${API.catalog}/api/v1/equipment/${id}`);
    el.innerHTML = `<div class="equipment-detail">
      <h2>${eq.name}</h2>
      <div class="subtitle">${eq.manufacturer} ${eq.model} (${eq.year}) | SKU: ${eq.sku}</div>
      <p>${eq.description}</p>
      <div class="detail-grid">
        <div><strong>Category:</strong> ${eq.category.replace(/_/g, ' ')}</div>
        <div><strong>Condition:</strong> ${eq.condition}</div>
        <div><strong>Hours Used:</strong> ${eq.hoursUsed}</div>
        <div><strong>Weight:</strong> ${eq.specifications?.weight} kg</div>
        <div><strong>Location:</strong> ${eq.availability?.[0]?.location?.city || 'N/A'}</div>
        <div><strong>Status:</strong> <span class="badge badge-${eq.availability?.[0]?.status || 'available'}">${eq.availability?.[0]?.status || 'available'}</span></div>
        <div><strong>Daily Rate:</strong> $${eq.pricing?.dailyRate}/day</div>
        <div><strong>Weekly Rate:</strong> $${eq.pricing?.weeklyRate}/week</div>
        <div><strong>Monthly Rate:</strong> $${eq.pricing?.monthlyRate}/month</div>
      </div>
      <div><strong>Features:</strong> ${(eq.features || []).join(', ')}</div>
      <div style="margin-top:8px"><strong>Deposit:</strong> $${eq.depositAmount || 0} | <strong>Insurance:</strong> ${eq.insuranceRequired ? 'Required' : 'Optional'} | <strong>Operator:</strong> ${eq.requiresOperator ? 'Required' : 'Optional'}</div>
      <button class="btn-order" onclick="showQuoteForm('${eq._id}', '${eq.name.replace(/'/g, "\\'")}', ${eq.pricing?.dailyRate || 0})">Request Quote</button>
    </div>`;
  } catch (e) {
    el.innerHTML = '<div class="loading">Failed to load equipment details.</div>';
  }
}

// ============= QUOTE FORM =============

function showQuoteForm(id, name, rate) {
  if (!getToken()) { toast('Please login first', 'error'); showPage('login'); return; }
  showPage('quote-create');
  document.getElementById('quote-equipment-id').value = id;
  document.getElementById('quote-equipment-name').textContent = name;
  document.getElementById('quote-daily-rate').textContent = rate;
  updateQuoteTotal();
}

function updateQuoteTotal() {
  const rate = parseFloat(document.getElementById('quote-daily-rate').textContent) || 0;
  const qty = parseInt(document.getElementById('quote-qty').value) || 1;
  const days = parseInt(document.getElementById('quote-days').value) || 1;
  const delivery = document.getElementById('quote-delivery').checked;
  const subtotal = rate * qty * days;
  const insurance = subtotal * 0.05;
  const deliveryFee = delivery ? subtotal * 0.10 : 0;
  const total = subtotal + insurance + deliveryFee;
  document.getElementById('quote-subtotal').textContent = subtotal.toFixed(2);
  document.getElementById('quote-insurance').textContent = insurance.toFixed(2);
  document.getElementById('quote-delivery-fee').textContent = deliveryFee.toFixed(2);
  document.getElementById('quote-total').textContent = total.toFixed(2);
}

async function createQuote(e) {
  e.preventDefault();
  const el = document.getElementById('quote-result');
  el.textContent = 'Creating quote...';
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  try {
    const resp = await api('POST', `${API.checkout}/api/v1/quotes/`, {
      customer_id: String(user.id || 1),
      customer_type: user.role === 'customer' ? 'individual' : 'company',
      items: [{
        equipment_id: document.getElementById('quote-equipment-id').value,
        quantity: parseInt(document.getElementById('quote-qty').value) || 1,
        rental_days: parseInt(document.getElementById('quote-days').value) || 1,
        unit_price: parseFloat(document.getElementById('quote-daily-rate').textContent) || 0,
      }],
      delivery_required: document.getElementById('quote-delivery').checked,
    });
    el.innerHTML = `<p style="color:#059669;font-weight:600">Quote created: ${resp.quote_id}</p>
      <p>Subtotal: $${resp.subtotal.toFixed(2)} | Total: $${resp.total.toFixed(2)}</p>
      <p>Valid until: ${new Date(resp.valid_until).toLocaleDateString()}</p>
      <button onclick="acceptQuote('${resp.quote_id}')">Accept Quote</button>`;
    toast('Quote created!', 'success');
  } catch (e) {
    el.innerHTML = `<p style="color:#dc2626">Failed to create quote: ${e.detail || e.error || 'Unknown error'}</p>`;
  }
}

async function acceptQuote(id) {
  try {
    const resp = await api('POST', `${API.checkout}/api/v1/quotes/${id}/accept`);
    toast('Quote accepted!', 'success');
    showPage('quotes');
  } catch (e) {
    toast(e.detail || 'Failed to accept quote', 'error');
  }
}

// ============= QUOTES =============

async function loadQuotes() {
  const el = document.getElementById('quotes-list');
  if (!getToken()) { el.innerHTML = '<p>Please login to view your quotes.</p>'; return; }
  el.innerHTML = '<div class="loading">Loading quotes...</div>';
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const data = await api('GET', `${API.checkout}/api/v1/quotes/?customer_id=${user.id || ''}`);
    if (!data.length) { el.innerHTML = '<p>No quotes yet. Browse equipment to create one.</p>'; return; }
    el.innerHTML = data.map(q => `<div class="quote-card">
      <h3>${q.quote_id}</h3>
      <div class="meta">Created: ${new Date(q.created_at).toLocaleDateString()} | Valid until: ${new Date(q.valid_until).toLocaleDateString()}</div>
      <div class="meta">Items: ${q.items.length} | Total: <strong>$${q.total.toFixed(2)}</strong></div>
      <span class="status-badge status-${q.status}">${q.status}</span>
      ${q.status === 'pending' ? `<button onclick="acceptQuote('${q.quote_id}')" style="margin-left:10px;padding:4px 12px;font-size:0.85rem">Accept</button>` : ''}
      ${q.status !== 'cancelled' ? `<button onclick="createOrder('${q.quote_id}')" style="margin-left:6px;padding:4px 12px;font-size:0.85rem">Create Order</button>` : ''}
    </div>`).join('');
  } catch (e) {
    el.innerHTML = '<p>Failed to load quotes.</p>';
  }
}

async function createOrder(quoteId) {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  try {
    const resp = await api('POST', `${API.checkout}/api/v1/orders/?quote_id=${quoteId}&customer_id=${user.id || 1}`);
    toast('Order created!', 'success');
    showPage('orders');
  } catch (e) {
    toast(e.detail || 'Failed to create order', 'error');
  }
}

// ============= ORDERS =============

async function loadOrders() {
  const el = document.getElementById('orders-list');
  if (!getToken()) { el.innerHTML = '<p>Please login to view your orders.</p>'; return; }
  el.innerHTML = '<div class="loading">Loading orders...</div>';
  try {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const data = await api('GET', `${API.checkout}/api/v1/orders/?customer_id=${user.id || ''}`);
    if (!data.length) { el.innerHTML = '<p>No orders yet. Accept a quote and create an order.</p>'; return; }
    el.innerHTML = data.map(o => `<div class="order-card">
      <h3>${o.order_id}</h3>
      <div class="meta">Quote: ${o.quote_id} | Created: ${new Date(o.created_at).toLocaleDateString()}</div>
      <div class="meta">Items: ${o.items.length} | Total: <strong>$${o.total.toFixed(2)}</strong></div>
      <span class="status-badge status-${o.status}">${o.status}</span>
      <span class="status-badge status-${o.payment_status === 'paid' ? 'accepted' : 'pending'}" style="margin-left:6px">Payment: ${o.payment_status}</span>
      ${o.status === 'pending' ? `<button onclick="confirmOrder('${o.order_id}')" style="margin-left:10px;padding:4px 12px;font-size:0.85rem">Confirm & Pay</button>` : ''}
      ${o.status !== 'completed' && o.status !== 'cancelled' ? `<button onclick="cancelOrder('${o.order_id}')" style="margin-left:6px;padding:4px 12px;font-size:0.85rem;background:#dc2626">Cancel</button>` : ''}
    </div>`).join('');
  } catch (e) {
    el.innerHTML = '<p>Failed to load orders.</p>';
  }
}

async function confirmOrder(orderId) {
  try {
    const resp = await api('POST', `${API.checkout}/api/v1/orders/${orderId}/confirm`);
    toast('Order confirmed! Payment processed.', 'success');
    loadOrders();
  } catch (e) {
    toast(e.detail || 'Payment failed', 'error');
    loadOrders();
  }
}

async function cancelOrder(orderId) {
  try {
    const resp = await api('POST', `${API.checkout}/api/v1/orders/${orderId}/cancel`);
    toast('Order cancelled', 'info');
    loadOrders();
  } catch (e) {
    toast(e.detail || 'Failed to cancel order', 'error');
  }
}

// ============= AUTH =============

async function login(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;
  try {
    const resp = await api('POST', `${API.users}/api/v1/users/login/`, { email, password });
    localStorage.setItem('access_token', resp.access);
    localStorage.setItem('refresh_token', resp.refresh);
    localStorage.setItem('user', JSON.stringify(resp.user));
    auth.token = resp.access;
    auth.user = resp.user;
    toast(`Welcome, ${resp.user.first_name}!`, 'success');
    showPage('catalog');
  } catch (e) {
    toast(e.detail || e.error || 'Login failed', 'error');
  }
}

async function register(e) {
  e.preventDefault();
  const p1 = document.getElementById('reg-password').value;
  const p2 = document.getElementById('reg-password2').value;
  if (p1 !== p2) { toast('Passwords do not match', 'error'); return; }
  try {
    await api('POST', `${API.users}/api/v1/users/`, {
      email: document.getElementById('reg-email').value,
      first_name: document.getElementById('reg-first').value,
      last_name: document.getElementById('reg-last').value,
      password: p1,
      password_confirm: p2,
      role: document.getElementById('reg-role').value,
    });
    toast('Registration successful! Please login.', 'success');
    showPage('login');
  } catch (e) {
    const msg = e.detail?.[0] || e.error || Object.values(e || {}).flat().join(', ') || 'Registration failed';
    toast(msg, 'error');
  }
}

// ============= INIT =============

const savedToken = localStorage.getItem('access_token');
const savedUser = localStorage.getItem('user');
if (savedToken) {
  auth.token = savedToken;
  auth.user = savedUser ? JSON.parse(savedUser) : null;
}
updateAuthUI();
loadEquipment();
