const API = {
  catalog: 'http://localhost:3000',
  users: 'http://localhost:8000',
  checkout: 'http://localhost:8001',
  payment: 'http://localhost:8100',
};

let auth = {
  token: null,
  user: null,
};

function getToken() {
  const t = localStorage.getItem('access_token');
  if (t) auth.token = t;
  return auth.token;
}

function getHeaders(withAuth = false) {
  const h = { 'Content-Type': 'application/json' };
  if (withAuth && getToken()) {
    h['Authorization'] = `Bearer ${getToken()}`;
  }
  return h;
}

async function api(method, url, body = null, withAuth = false) {
  const opts = { method, headers: getHeaders(withAuth) };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(url, opts);
  const data = await res.json();
  if (!res.ok) throw { status: res.status, ...data };
  return data;
}
