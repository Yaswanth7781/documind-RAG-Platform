import React, { useState } from 'react';
import { User, Lock, KeyRound, ShieldAlert } from 'lucide-react';
import { loginUser, signupUser } from '../services/api';
import './LoginSignup.css';

export default function LoginSignup({ onLoginSuccess }) {
  const [isLogin, setIsLogin] = useState(true);
  const [regNo, setRegNo] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState('Student');
  const [adminPin, setAdminPin] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setIsLoading(true);

    try {
      if (isLogin) {
        const data = await loginUser(regNo, password);
        onLoginSuccess(data);
      } else {
        await signupUser(regNo, password, role, adminPin);
        setMessage('Registration successful! Please login.');
        setIsLogin(true);
        setPassword('');
        setAdminPin('');
      }
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-signup-wrapper">
      <div className="auth-card glass animate-fade-in">
        <div className="auth-header">
          <h1 className="auth-brand">Uni<span className="text-accent">Guard</span> <span className="auth-sub">AI</span></h1>
          <p className="auth-tagline">Compliance & Intelligence Platform</p>
        </div>

        <div className="auth-tabs">
          <button 
            type="button" 
            className={`auth-tab ${isLogin ? 'active' : ''}`} 
            onClick={() => { setIsLogin(true); setError(''); setMessage(''); }}
          >
            Login
          </button>
          <button 
            type="button" 
            className={`auth-tab ${!isLogin ? 'active' : ''}`} 
            onClick={() => { setIsLogin(false); setError(''); setMessage(''); }}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="auth-alert error"><ShieldAlert size={18} /> <span>{error}</span></div>}
          {message && <div className="auth-alert success"><span>{message}</span></div>}

          <div className="input-group">
            <label>Registration Number</label>
            <div className="input-field-wrapper">
              <User size={18} className="input-icon" />
              <input
                type="text"
                placeholder="e.g. 12313297"
                value={regNo}
                onChange={(e) => setRegNo(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="input-group">
            <label>Password</label>
            <div className="input-field-wrapper">
              <Lock size={18} className="input-icon" />
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {!isLogin && (
            <>
              <div className="input-group">
                <label>Select Role</label>
                <div className="input-field-wrapper">
                  <select value={role} onChange={(e) => setRole(e.target.value)} className="auth-select">
                    <option value="Student">👨‍🎓 Student</option>
                    <option value="Faculty">👨‍🏫 Faculty</option>
                    <option value="Admin">🛡️ Admin</option>
                  </select>
                </div>
              </div>

              {role === 'Admin' && (
                <div className="input-group animate-fade-in">
                  <label>Admin Security PIN</label>
                  <div className="input-field-wrapper">
                    <KeyRound size={18} className="input-icon" />
                    <input
                      type="password"
                      placeholder="Enter Security PIN"
                      value={adminPin}
                      onChange={(e) => setAdminPin(e.target.value)}
                      required
                    />
                  </div>
                </div>
              )}
            </>
          )}

          <button type="submit" className="auth-submit-btn" disabled={isLoading}>
            {isLoading ? 'Processing...' : isLogin ? 'Sign In' : 'Register Account'}
          </button>
        </form>
      </div>
    </div>
  );
}
