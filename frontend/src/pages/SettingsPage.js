import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FiUser, FiPhone, FiMapPin, FiBell, FiMoon, FiSun,
  FiShield, FiDatabase, FiSave, FiLogOut
} from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import toast from 'react-hot-toast';
import './SettingsPage.css';

const SettingsPage = () => {
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  
  const [profile, setProfile] = useState({
    name: user?.name || '',
    phone: user?.phone || '',
    address: user?.address || '',
    city: user?.city || '',
    state: user?.state || '',
    pincode: user?.pincode || ''
  });

  const [notifications, setNotifications] = useState({
    sms_alerts: true,
    critical_only: false,
    daily_report: true,
    weekly_summary: true
  });

  const [thresholds, setThresholds] = useState({
    ph_min: 6.5,
    ph_max: 8.5,
    tds_max: 500,
    turbidity_max: 5,
    water_level_min: 20
  });

  const handleSaveProfile = () => {
    // In production, call API
    toast.success('Profile updated successfully!');
  };

  const handleSaveNotifications = () => {
    toast.success('Notification preferences saved!');
  };

  const handleSaveThresholds = () => {
    toast.success('Alert thresholds updated!');
  };

  return (
    <div className="settings-page">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p>Manage your account and preferences</p>
        </div>
      </div>

      <div className="settings-grid">
        {/* Profile Section */}
        <motion.div 
          className="card settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="section-header">
            <FiUser size={20} />
            <h2>Profile Information</h2>
          </div>

          <div className="profile-avatar">
            <img 
              src={user?.picture || `https://ui-avatars.com/api/?name=${user?.name}&background=0ea5e9&color=fff`}
              alt={user?.name}
            />
            <div className="profile-info">
              <h3>{user?.name}</h3>
              <p>{user?.email}</p>
            </div>
          </div>

          <div className="form-grid">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                value={profile.name}
                onChange={e => setProfile({...profile, name: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label className="form-label">Phone Number</label>
              <input
                type="tel"
                className="form-input"
                value={profile.phone}
                onChange={e => setProfile({...profile, phone: e.target.value})}
                placeholder="+91 XXXXX XXXXX"
              />
            </div>
            <div className="form-group full-width">
              <label className="form-label">Address</label>
              <input
                type="text"
                className="form-input"
                value={profile.address}
                onChange={e => setProfile({...profile, address: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label className="form-label">City</label>
              <input
                type="text"
                className="form-input"
                value={profile.city}
                onChange={e => setProfile({...profile, city: e.target.value})}
              />
            </div>
            <div className="form-group">
              <label className="form-label">State</label>
              <input
                type="text"
                className="form-input"
                value={profile.state}
                onChange={e => setProfile({...profile, state: e.target.value})}
              />
            </div>
          </div>

          <button className="btn btn-primary" onClick={handleSaveProfile}>
            <FiSave /> Save Changes
          </button>
        </motion.div>

        {/* Notifications Section */}
        <motion.div 
          className="card settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="section-header">
            <FiBell size={20} />
            <h2>Notifications</h2>
          </div>

          <div className="toggle-list">
            <div className="toggle-item">
              <div className="toggle-info">
                <h4>SMS Alerts</h4>
                <p>Receive SMS notifications for water quality issues</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={notifications.sms_alerts}
                  onChange={e => setNotifications({...notifications, sms_alerts: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="toggle-item">
              <div className="toggle-info">
                <h4>Critical Alerts Only</h4>
                <p>Only notify for critical water quality issues</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={notifications.critical_only}
                  onChange={e => setNotifications({...notifications, critical_only: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="toggle-item">
              <div className="toggle-info">
                <h4>Daily Report</h4>
                <p>Receive daily water quality summary</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={notifications.daily_report}
                  onChange={e => setNotifications({...notifications, daily_report: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>

            <div className="toggle-item">
              <div className="toggle-info">
                <h4>Weekly Summary</h4>
                <p>Receive weekly analytics and insights</p>
              </div>
              <label className="toggle">
                <input
                  type="checkbox"
                  checked={notifications.weekly_summary}
                  onChange={e => setNotifications({...notifications, weekly_summary: e.target.checked})}
                />
                <span className="toggle-slider"></span>
              </label>
            </div>
          </div>

          <button className="btn btn-primary" onClick={handleSaveNotifications}>
            <FiSave /> Save Preferences
          </button>
        </motion.div>

        {/* Appearance Section */}
        <motion.div 
          className="card settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="section-header">
            {isDark ? <FiMoon size={20} /> : <FiSun size={20} />}
            <h2>Appearance</h2>
          </div>

          <div className="theme-selector">
            <button
              className={`theme-option ${!isDark ? 'active' : ''}`}
              onClick={() => !isDark || toggleTheme()}
            >
              <FiSun size={24} />
              <span>Light Mode</span>
            </button>
            <button
              className={`theme-option ${isDark ? 'active' : ''}`}
              onClick={() => isDark || toggleTheme()}
            >
              <FiMoon size={24} />
              <span>Dark Mode</span>
            </button>
          </div>
        </motion.div>

        {/* Alert Thresholds Section */}
        <motion.div 
          className="card settings-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="section-header">
            <FiShield size={20} />
            <h2>Alert Thresholds</h2>
          </div>

          <div className="threshold-list">
            <div className="threshold-item">
              <label>pH Range</label>
              <div className="threshold-inputs">
                <input
                  type="number"
                  step="0.1"
                  value={thresholds.ph_min}
                  onChange={e => setThresholds({...thresholds, ph_min: parseFloat(e.target.value)})}
                />
                <span>to</span>
                <input
                  type="number"
                  step="0.1"
                  value={thresholds.ph_max}
                  onChange={e => setThresholds({...thresholds, ph_max: parseFloat(e.target.value)})}
                />
              </div>
            </div>

            <div className="threshold-item">
              <label>Max TDS (mg/L)</label>
              <input
                type="number"
                value={thresholds.tds_max}
                onChange={e => setThresholds({...thresholds, tds_max: parseInt(e.target.value)})}
              />
            </div>

            <div className="threshold-item">
              <label>Max Turbidity (NTU)</label>
              <input
                type="number"
                step="0.1"
                value={thresholds.turbidity_max}
                onChange={e => setThresholds({...thresholds, turbidity_max: parseFloat(e.target.value)})}
              />
            </div>

            <div className="threshold-item">
              <label>Min Water Level (%)</label>
              <input
                type="number"
                value={thresholds.water_level_min}
                onChange={e => setThresholds({...thresholds, water_level_min: parseInt(e.target.value)})}
              />
            </div>
          </div>

          <button className="btn btn-primary" onClick={handleSaveThresholds}>
            <FiSave /> Save Thresholds
          </button>
        </motion.div>

        {/* Danger Zone */}
        <motion.div 
          className="card settings-section danger-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="section-header">
            <FiLogOut size={20} />
            <h2>Account</h2>
          </div>

          <p className="danger-text">
            Sign out of your account on this device.
          </p>

          <button className="btn btn-danger" onClick={logout}>
            <FiLogOut /> Sign Out
          </button>
        </motion.div>
      </div>
    </div>
  );
};

export default SettingsPage;
