const API_BASE = '/api';

const TOKEN_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

function getAccessToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function getRefreshToken() {
    return localStorage.getItem(REFRESH_KEY);
}

function setTokens(access, refresh) {
    localStorage.setItem(TOKEN_KEY, access);
    if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

function clearTokens() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_KEY);
}

function isAuthenticated() {
    return !!getAccessToken();
}

async function refreshAccessToken() {
    const refresh = getRefreshToken();
    if (!refresh) return null;
    try {
        const res = await fetch(`${API_BASE}/users/login/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh })
        });
        if (!res.ok) return null;
        const data = await res.json();
        setTokens(data.access, refresh);
        return data.access;
    } catch {
        return null;
    }
}

async function apiRequest(url, options = {}) {
    const token = getAccessToken();
    const headers = { ...options.headers };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    if (!(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    let res = await fetch(`${API_BASE}${url}`, { ...options, headers });

    if (res.status === 401 && token) {
        const newToken = await refreshAccessToken();
        if (newToken) {
            headers['Authorization'] = `Bearer ${newToken}`;
            res = await fetch(`${API_BASE}${url}`, { ...options, headers });
        } else {
            clearTokens();
            window.location.href = '/login/';
            throw new Error('Session expired');
        }
    }

    return res;
}
