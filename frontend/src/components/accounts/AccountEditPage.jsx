/**
 * Account Edit Page Component
 * Allows users to edit their profile information
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './AccountStyles.css';

const AccountEditPage = () => {
  const { user, updateProfile, changePassword, updateEmail, logout } = useAuth();
  const navigate = useNavigate();

  // Profile form state
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    phone: '',
    bio: '',
    profile_image: '',
  });

  // Password form state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // Email form state
  const [emailData, setEmailData] = useState({
    new_email: '',
    password: '',
  });

  // UI state
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');

  // Initialize form with user data
  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        phone: user.phone || '',
        bio: user.bio || '',
        profile_image: user.profile_image || '',
      });
      setEmailData(prev => ({ ...prev, new_email: user.email }));
    }
  }, [user]);

  const clearMessages = () => {
    setSuccess('');
    setError('');
  };

  // Profile handlers
  const handleProfileChange = (e) => {
    const { name, value } = e.target;
    setProfileData(prev => ({ ...prev, [name]: value }));
    clearMessages();
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    clearMessages();

    try {
      await updateProfile(profileData);
      setSuccess('Profile updated successfully!');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Password handlers
  const handlePasswordChange = (e) => {
    const { name, value } = e.target;
    setPasswordData(prev => ({ ...prev, [name]: value }));
    clearMessages();
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    clearMessages();

    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('New passwords do not match');
      setLoading(false);
      return;
    }

    try {
      await changePassword(passwordData.current_password, passwordData.new_password);
      setSuccess('Password changed successfully!');
      setPasswordData({
        current_password: '',
        new_password: '',
        confirm_password: '',
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Email handlers
  const handleEmailChange = (e) => {
    const { name, value } = e.target;
    setEmailData(prev => ({ ...prev, [name]: value }));
    clearMessages();
  };

  const handleEmailSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    clearMessages();

    try {
      await updateEmail(emailData.new_email, emailData.password);
      setSuccess('Email updated successfully!');
      setEmailData(prev => ({ ...prev, password: '' }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getRoleBadgeClass = (role) => {
    switch (role) {
      case 'admin': return 'badge-admin';
      case 'teacher': return 'badge-teacher';
      case 'student': return 'badge-student';
      default: return '';
    }
  };

  if (!user) {
    return (
      <div className="edit-container">
        <div className="loading-state">Loading...</div>
      </div>
    );
  }

  return (
    <div className="edit-container">
      <div className="edit-page">
        {/* Header */}
        <div className="edit-header">
          <button className="btn btn-ghost" onClick={() => navigate('/dashboard')}>
            ← Back to Dashboard
          </button>
          <h1>Account Settings</h1>
        </div>

        {/* Profile Summary Card */}
        <div className="profile-summary">
          <div className="avatar-large">
            {user.profile_image ? (
              <img src={user.profile_image} alt={user.full_name} />
            ) : (
              <span>{user.first_name?.[0]}{user.last_name?.[0]}</span>
            )}
          </div>
          <div className="profile-info">
            <h2>{user.full_name}</h2>
            <p className="profile-email">{user.email}</p>
            <span className={`badge ${getRoleBadgeClass(user.role)}`}>
              {user.role}
            </span>
          </div>
        </div>

        {/* Messages */}
        {success && (
          <div className="alert alert-success">
            <span className="alert-icon">✓</span>
            {success}
          </div>
        )}
        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠️</span>
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
            onClick={() => { setActiveTab('profile'); clearMessages(); }}
          >
            <span className="tab-icon">👤</span>
            Profile
          </button>
          <button 
            className={`tab ${activeTab === 'security' ? 'active' : ''}`}
            onClick={() => { setActiveTab('security'); clearMessages(); }}
          >
            <span className="tab-icon">🔒</span>
            Security
          </button>
          <button 
            className={`tab ${activeTab === 'email' ? 'active' : ''}`}
            onClick={() => { setActiveTab('email'); clearMessages(); }}
          >
            <span className="tab-icon">📧</span>
            Email
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <form onSubmit={handleProfileSubmit} className="edit-form">
              <h3>Personal Information</h3>
              
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="first_name">First Name</label>
                  <input
                    type="text"
                    id="first_name"
                    name="first_name"
                    value={profileData.first_name}
                    onChange={handleProfileChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="last_name">Last Name</label>
                  <input
                    type="text"
                    id="last_name"
                    name="last_name"
                    value={profileData.last_name}
                    onChange={handleProfileChange}
                    required
                  />
                </div>
              </div>

              <div className="form-group">
                <label htmlFor="phone">Phone Number</label>
                <input
                  type="tel"
                  id="phone"
                  name="phone"
                  value={profileData.phone}
                  onChange={handleProfileChange}
                  placeholder="+1 (555) 123-4567"
                />
              </div>

              <div className="form-group">
                <label htmlFor="profile_image">Profile Image URL</label>
                <input
                  type="url"
                  id="profile_image"
                  name="profile_image"
                  value={profileData.profile_image}
                  onChange={handleProfileChange}
                  placeholder="https://example.com/avatar.jpg"
                />
              </div>

              <div className="form-group">
                <label htmlFor="bio">Bio</label>
                <textarea
                  id="bio"
                  name="bio"
                  value={profileData.bio}
                  onChange={handleProfileChange}
                  rows={4}
                  placeholder="Tell us about yourself..."
                />
              </div>

              <div className="form-actions">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </form>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <form onSubmit={handlePasswordSubmit} className="edit-form">
              <h3>Change Password</h3>
              
              <div className="form-group">
                <label htmlFor="current_password">Current Password</label>
                <input
                  type="password"
                  id="current_password"
                  name="current_password"
                  value={passwordData.current_password}
                  onChange={handlePasswordChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="new_password">New Password</label>
                <input
                  type="password"
                  id="new_password"
                  name="new_password"
                  value={passwordData.new_password}
                  onChange={handlePasswordChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirm_password">Confirm New Password</label>
                <input
                  type="password"
                  id="confirm_password"
                  name="confirm_password"
                  value={passwordData.confirm_password}
                  onChange={handlePasswordChange}
                  required
                />
              </div>

              <p className="password-hint">
                Password must be at least 8 characters with uppercase, lowercase, and a number.
              </p>

              <div className="form-actions">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Updating...' : 'Update Password'}
                </button>
              </div>
            </form>
          )}

          {/* Email Tab */}
          {activeTab === 'email' && (
            <form onSubmit={handleEmailSubmit} className="edit-form">
              <h3>Change Email Address</h3>
              
              <div className="form-group">
                <label htmlFor="new_email">New Email Address</label>
                <input
                  type="email"
                  id="new_email"
                  name="new_email"
                  value={emailData.new_email}
                  onChange={handleEmailChange}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="email_password">Current Password</label>
                <input
                  type="password"
                  id="email_password"
                  name="password"
                  value={emailData.password}
                  onChange={handleEmailChange}
                  placeholder="Enter your password to confirm"
                  required
                />
              </div>

              <div className="form-actions">
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Updating...' : 'Update Email'}
                </button>
              </div>
            </form>
          )}
        </div>

        {/* Danger Zone */}
        <div className="danger-zone">
          <h3>Danger Zone</h3>
          <p>Once you deactivate your account, you will no longer be able to access it.</p>
          <button 
            className="btn btn-danger"
            onClick={() => {
              if (window.confirm('Are you sure you want to deactivate your account?')) {
                logout();
                navigate('/login');
              }
            }}
          >
            Deactivate Account
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountEditPage;






