// src/components/Sidebar.jsx
import React, { useRef, useState, useEffect } from 'react';
import { UploadCloud, CheckCircle, FileText, Trash2 } from 'lucide-react';
import { uploadPDF, fetchDocuments, deleteDocument, loginAdmin } from '../services/api';
import './Sidebar.css';

export default function Sidebar({ onUploadSuccess, userRole, regNo, token, activeTab, setActiveTab, onLogout, isOpen, closeMobile }) {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [documents, setDocuments] = useState([]);

  const loadDocuments = async () => {
    try {
      const data = await fetchDocuments();
      if (data && data.documents) {
        setDocuments(data.documents);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (userRole === 'Admin') {
      loadDocuments();
    }
  }, [userRole]);

  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      for (const file of files) {
        await uploadPDF(file, token);
      }
      await loadDocuments(); // Refresh the list from the database
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      console.error(err);
      alert("Failed to upload PDFs. Please check your credentials or network.");
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  const handleDelete = async (filename) => {
    try {
      await deleteDocument(filename, token);
      await loadDocuments(); // Refresh the list
    } catch (err) {
      alert(`Failed to delete ${filename}`);
    }
  };

  return (
    <>
      {isOpen && <div className="mobile-overlay" onClick={() => closeMobile(false)} style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(17,20,57,0.5)', zIndex: 9000 }} />}
      <aside className={`sidebar glass ${isOpen ? 'mobile-open' : ''}`}>
        <div className="sidebar-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 className="brand-logo" style={{ marginBottom: 0 }}>Uni<span className="text-accent">Guard</span> <span style={{ fontSize: '0.8rem', fontWeight: '500', marginLeft: '0.3rem', color: 'var(--text-secondary)' }}>AI</span></h2>
          <button className="hidden-desktop menu-btn" onClick={() => closeMobile(false)} style={{ fontSize: '1.5rem', background: 'none', border: 'none', color: 'var(--text-primary)' }}>✕</button>
        </div>

        {/* User Info Card */}
        <div className="user-profile-card glass" style={{ margin: '0 1.5rem 1.5rem 1.5rem', padding: '0.85rem 1rem', borderRadius: '8px', background: 'rgba(0,0,0,0.02)', border: '1px solid var(--border-color)' }}>
          <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.5px' }}>Logged In As</div>
          <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', margin: '0.15rem 0' }}>{regNo}</div>
          <span className={`role-tag ${userRole.toLowerCase()}`} style={{ display: 'inline-block', marginTop: '0.25rem', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 700 }}>
            {userRole === 'Admin' ? '🛡️ Admin' : userRole === 'Faculty' ? '👨‍🏫 Faculty' : '👨‍🎓 Student'}
          </span>
        </div>

        {/* Admin Navigation Tabs */}
        {userRole === 'Admin' && (
          <div className="admin-nav-tabs" style={{ margin: '0 1.5rem 1.5rem 1.5rem', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <div style={{ fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600, color: 'var(--text-secondary)', letterSpacing: '0.5px', marginBottom: '0.25rem' }}>Navigation</div>
            <button
              onClick={() => setActiveTab('chat')}
              className={`nav-tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
              style={{ width: '100%', padding: '0.65rem 1rem', textAlign: 'left', borderRadius: '6px', fontSize: '0.9rem', fontWeight: 600, transition: 'all 0.3s ease' }}
            >
              💬 Compliance Chat
            </button>
            <button
              onClick={() => setActiveTab('audit')}
              className={`nav-tab-btn ${activeTab === 'audit' ? 'active' : ''}`}
              style={{ width: '100%', padding: '0.65rem 1rem', textAlign: 'left', borderRadius: '6px', fontSize: '0.9rem', fontWeight: 600, transition: 'all 0.3s ease' }}
            >
              📋 System Audit Logs
            </button>
          </div>
        )}

        {/* Admin File Upload & Active PDFs Section */}
        {userRole === 'Admin' && activeTab === 'chat' && (
          <>
            <div className="upload-container">
              <input
                type="file"
                accept="application/pdf"
                multiple
                ref={fileInputRef}
                style={{ display: 'none' }}
                onChange={handleFileChange}
              />
              <div
                className="upload-dropzone glass"
                onClick={() => fileInputRef.current?.click()}
              >
                {isUploading ? (
                  <div className="uploading-state">
                    <UploadCloud className="icon animate-pulse" size={32} />
                    <p>Uploading...</p>
                  </div>
                ) : (
                  <div className="initial-state animate-fade-in">
                    <UploadCloud className="icon" size={32} color="var(--accent-color)" />
                    <p>Click to upload Policy PDF</p>
                  </div>
                )}
              </div>
            </div>

            {documents.length > 0 && (
              <div className="document-list animate-fade-in">
                <h3 className="section-title">Active Documents</h3>
                <div className="docs-container">
                  {documents.map((doc, idx) => (
                    <div key={idx} className="doc-item glass">
                      <FileText size={16} color="var(--accent-color)" />
                      <span className="doc-name" title={doc}>{doc}</span>
                      <button className="del-btn" onClick={() => handleDelete(doc)} title="Remove document">
                        <Trash2 size={16} color="var(--error-color)" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </>
        )}

        <div className="sidebar-footer" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', padding: '1rem 1.5rem' }}>
          <button
            onClick={onLogout}
            className="logout-btn glass"
            style={{ width: '100%', padding: '0.6rem', background: 'rgba(239, 68, 68, 0.08)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444', borderRadius: '6px', fontWeight: 600, fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem', transition: 'all 0.3s ease' }}
          >
            🚪 Sign Out
          </button>
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>System Online</span>
          </div>
        </div>
      </aside>
    </>
  );
}
