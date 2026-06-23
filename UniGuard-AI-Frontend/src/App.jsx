// src/App.jsx
import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import LoginSignup from './components/LoginSignup';
import AuditLogs from './components/AuditLogs';
import { Menu, X } from 'lucide-react'; //ham burger menu icons
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [userRole, setUserRole] = useState(localStorage.getItem('role') || 'Student');
  const [regNo, setRegNo] = useState(localStorage.getItem('regNo') || '');
  const [activeTab, setActiveTab] = useState('chat');
  const [isReady, setIsReady] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLoginSuccess = (data) => {
    localStorage.setItem('token', data.access_token);
    localStorage.setItem('role', data.role);
    localStorage.setItem('regNo', data.reg_no);
    setToken(data.access_token);
    setUserRole(data.role);
    setRegNo(data.reg_no);
    setActiveTab('chat');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    localStorage.removeItem('regNo');
    setToken(null);
    setUserRole('Student');
    setRegNo('');
    setActiveTab('chat');
  };

  const handleUploadSuccess = (data) => {
    console.log("Upload Success:", data);
    setIsReady(true);
  };

  // 1. Unauthenticated view: Render signup/login
  if (!token) {
    return <LoginSignup onLoginSuccess={handleLoginSuccess} />;
  }

  // 2. Authenticated view
  return (
    <div className="app-container">
      {/* Mobile Top Bar */}
      <div className="mobile-topbar hidden-desktop glass">
        <h2 className="brand-logo" style={{ marginBottom: 0, fontSize: '1.2rem' }}>
          Uni<span className="text-accent">Guard</span> <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>AI</span>
        </h2>
        <button className="menu-btn" onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}>
          {isMobileMenuOpen ? <X size={24} color="var(--text-primary)" /> : <Menu size={24} color="var(--text-primary)" />}
        </button>
      </div>

      <Sidebar
        onUploadSuccess={handleUploadSuccess}
        userRole={userRole}
        regNo={regNo}
        token={token}
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onLogout={handleLogout}
        isOpen={isMobileMenuOpen}
        closeMobile={setIsMobileMenuOpen}
      />
      
      {userRole === 'Admin' && activeTab === 'audit' ? (
        <AuditLogs token={token} />
      ) : (
        <ChatArea isReady={isReady} userRole={userRole} regNo={regNo} />
      )}
    </div>
  );
}

export default App;
