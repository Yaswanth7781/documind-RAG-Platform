// src/services/api.js

const HOSTNAME = window.location.hostname;
const API_URL = import.meta.env.VITE_API_URL || `http://${HOSTNAME}:8000`;

const AUTH_API_URL = API_URL;
const DOCUMENT_API_URL = API_URL;
const CHAT_API_URL = API_URL;

export const signupUser = async (regNo, password, role, adminPin) => {
  try {
    const response = await fetch(`${AUTH_API_URL}/auth/signup`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reg_no: regNo, password, role, admin_pin: adminPin })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `Signup failed: ${response.status}`);
    return data;
  } catch (error) {
    console.error('Signup Error:', error);
    throw error;
  }
};

export const loginUser = async (regNo, password) => {
  try {
    const response = await fetch(`${AUTH_API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reg_no: regNo, password })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `Login failed: ${response.status}`);
    return data;
  } catch (error) {
    console.error('Login Error:', error);
    throw error;
  }
};

export const fetchAuditLogs = async (token) => {
  try {
    const response = await fetch(`${AUTH_API_URL}/audit/list`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || `Fetch audit logs failed: ${response.status}`);
    return data;
  } catch (error) {
    console.error('Fetch Audit Logs Error:', error);
    throw error;
  }
};

export const uploadPDF = async (file, token) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch(`${DOCUMENT_API_URL}/documents/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData,
    });

    if (!response.ok) throw new Error(`Upload failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Upload Error:', error);
    throw error;
  }
};

export const fetchDocuments = async () => {
  try {
    const response = await fetch(`${DOCUMENT_API_URL}/documents/list`);
    if (!response.ok) throw new Error(`Fetch docs failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Fetch Docs Error:', error);
    throw error;
  }
};

export const deleteDocument = async (filename, token) => {
  try {
    const response = await fetch(`${DOCUMENT_API_URL}/documents/${filename}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    if (!response.ok) throw new Error(`Delete failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Delete Error:', error);
    throw error;
  }
}

export const chatWithAI = async (message, history = [], role = 'Student', regNo = null) => {
  try {
    const response = await fetch(`${CHAT_API_URL}/ai/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        prompt: message,
        history: history,
        role: role,
        reg_no: regNo
      }),
    });

    if (!response.ok) throw new Error(`Chat failed: ${response.status}`);
    return await response.json();
  } catch (error) {
    console.error('Chat Error:', error);
    throw error;
  }
};
