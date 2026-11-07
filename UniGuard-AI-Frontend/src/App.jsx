// src/App.jsx
import React, { useEffect, useState } from 'react';
import Sidebar from './components/Sidebar';
import ChatArea from './components/ChatArea';
import LoginSignup from './components/LoginSignup';
import AuditLogs from './components/AuditLogs';
import { FileText, Menu, Trash2, X } from 'lucide-react'; //ham burger menu icons
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [userRole, setUserRole] = useState(localStorage.getItem('role') || 'Student');
  const [regNo, setRegNo] = useState(localStorage.getItem('regNo') || '');
  const [activeTab, setActiveTab] = useState('chat');
  const [isReady, setIsReady] = useState(false);
  const [uploadedDocuments, setUploadedDocuments] = useState([]);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleAuthExpired = () => {
      setToken(null);
      setUserRole('Student');
      setRegNo('');
      setActiveTab('chat');
    };

    window.addEventListener('auth-expired', handleAuthExpired);
    return () => window.removeEventListener('auth-expired', handleAuthExpired);
  }, []);

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

  const handleDocumentsLoaded = (docs) => {
    setUploadedDocuments(docs || []);
    if (docs && docs.length > 0) {
      setIsReady(true);
    }
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
        onDocumentsLoaded={handleDocumentsLoaded}
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
      ) : userRole === 'Admin' && activeTab === 'documents' ? (
        <main className="chat-area animate-fade-in">
          <div className="messages-container">
            <div className="message-content-group">
              <div className="message-bubble glass ai-bubble">
                <h2 style={{ margin: 0 }}>Uploaded Documents</h2>
                <p style={{ marginBottom: 0, color: 'var(--text-secondary)' }}>
                  {uploadedDocuments.length} policy document{uploadedDocuments.length === 1 ? '' : 's'} available.
                </p>
              </div>
              <div className="documents-page-list">
                {uploadedDocuments.length === 0 ? (
                  <div className="message-bubble glass ai-bubble">
                    No uploaded documents found.
                  </div>
                ) : (
                  uploadedDocuments.map(documentName => (
                    <div className="document-page-item glass" key={documentName}>
                      <FileText size={20} color="var(--accent-color)" />
                      <span title={documentName}>{documentName}</span>
                      <button
                        className="document-delete-btn"
                        title={`Remove ${documentName}`}
                        aria-label={`Delete ${documentName}`}
                        onClick={() => window.dispatchEvent(new CustomEvent('delete-document', { detail: documentName }))}
                      >
                        <Trash2 size={18} />
                        <span>Delete</span>
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </main>
      ) : (
        <ChatArea isReady={isReady} userRole={userRole} regNo={regNo} />
      )}
    </div>
  );
}

export default App;
