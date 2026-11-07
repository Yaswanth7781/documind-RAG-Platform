// src/components/Sidebar.jsx
import React, { useRef, useState, useEffect } from 'react';
import { UploadCloud, CheckCircle, FileText, Trash2, X } from 'lucide-react';
import { uploadPDF, fetchDocuments, deleteDocument } from '../services/api';
import './Sidebar.css';

export default function Sidebar({ onUploadSuccess, onDocumentsLoaded, userRole, regNo, token, activeTab, setActiveTab, onLogout, isOpen, closeMobile }) {
  const fileInputRef = useRef(null);
  const [isUploading, setIsUploading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [documentToDelete, setDocumentToDelete] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const isAdmin = userRole === 'Admin';

  const loadDocuments = async () => {
    if (!isAdmin) {
      setDocuments([]);
      return;
    }

    try {
      const data = await fetchDocuments(token);
      const documentList = Array.isArray(data?.documents)
        ? data.documents.filter(Boolean)
        : [];
      setDocuments(documentList);
      if (onDocumentsLoaded) onDocumentsLoaded(documentList);
      return documentList;
    } catch (err) {
      console.error("Error loading documents:", err);
      if (token) alert(`Could not load documents: ${err.message}`);
      return [];
    }
  };

  const refreshDocumentsAfterUpload = async () => {
    for (let attempt = 0; attempt < 3; attempt += 1) {
      const documentList = await loadDocuments();
      if (documentList.length > 0) return;
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  };

  useEffect(() => {
    loadDocuments();
  }, [userRole, token]);

  useEffect(() => {
    const handleDocumentDelete = (event) => handleDelete(event.detail);
    window.addEventListener('delete-document', handleDocumentDelete);
    return () => window.removeEventListener('delete-document', handleDocumentDelete);
  }, [token]);

  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files);
    if (!files || files.length === 0) return;

    setIsUploading(true);
    try {
      for (const file of files) {
        await uploadPDF(file, token);
      }
      await refreshDocumentsAfterUpload();
      if (onUploadSuccess) onUploadSuccess();
    } catch (err) {
      console.error(err);
      alert(`Failed to upload PDF: ${err.message}`);
    } finally {
      setIsUploading(false);
      e.target.value = null;
    }
  };

  const handleDelete = (filename) => {
    setDocumentToDelete(filename);
  };

  const confirmDelete = async () => {
    if (!documentToDelete) return;

    setIsDeleting(true);
    try {
      await deleteDocument(documentToDelete, token);
      await loadDocuments(); // Refresh the list
      setDocumentToDelete(null);
    } catch (err) {
      alert(`Failed to delete ${documentToDelete}: ${err.message}`);
    } finally {
      setIsDeleting(false);
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
            <button
              onClick={() => setActiveTab('documents')}
              className={`nav-tab-btn ${activeTab === 'documents' ? 'active' : ''}`}
              style={{ width: '100%', padding: '0.65rem 1rem', textAlign: 'left', borderRadius: '6px', fontSize: '0.9rem', fontWeight: 600, transition: 'all 0.3s ease' }}
            >
              📄 Uploaded Documents
            </button>
          </div>
        )}

        {/* File Upload & Active PDFs Section */}
        {activeTab === 'documents' && isAdmin && (
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
                <h3 className="section-title">Active Documents ({documents.length})</h3>
                <div className="docs-container">
                  {documents.map((doc, idx) => (
                    <div key={idx} className="doc-item glass">
                      <FileText size={16} color="var(--accent-color)" />
                      <span className="doc-name" title={doc}>{doc}</span>
                      <button className="document-delete-btn" onClick={() => handleDelete(doc)} title={`Remove ${doc}`} aria-label={`Delete ${doc}`}>
                        <Trash2 size={16} />
                        <span>Delete</span>
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

      {documentToDelete && (
        <div className="delete-modal-overlay" role="presentation" onClick={() => !isDeleting && setDocumentToDelete(null)}>
          <div className="delete-modal" role="dialog" aria-modal="true" aria-labelledby="delete-document-title" onClick={(event) => event.stopPropagation()}>
            <button
              className="delete-modal-close"
              type="button"
              onClick={() => setDocumentToDelete(null)}
              disabled={isDeleting}
              aria-label="Close delete dialog"
            >
              <X size={20} />
            </button>
            <div className="delete-modal-icon"><Trash2 size={32} /></div>
            <h2 id="delete-document-title">Delete Document?</h2>
            <p>Are you sure you want to delete</p>
            <strong title={documentToDelete}>"{documentToDelete}"?</strong>
            <p>This action cannot be undone.</p>
            <div className="delete-modal-actions">
              <button type="button" className="delete-cancel-btn" onClick={() => setDocumentToDelete(null)} disabled={isDeleting}>
                Cancel
              </button>
              <button type="button" className="delete-confirm-btn" onClick={confirmDelete} disabled={isDeleting}>
                <Trash2 size={18} />
                {isDeleting ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
