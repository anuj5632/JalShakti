import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiHome, FiDroplet, FiAlertTriangle, FiBarChart2, 
  FiSettings, FiLogOut, FiMenu, FiX, FiSun, FiMoon 
} from 'react-icons/fi';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import './Sidebar.css';

const navItems = [
  { path: '/dashboard', icon: FiHome, label: 'Dashboard' },
  { path: '/sources', icon: FiDroplet, label: 'Water Sources' },
  { path: '/alerts', icon: FiAlertTriangle, label: 'Alerts' },
  { path: '/analytics', icon: FiBarChart2, label: 'Analytics' },
  { path: '/settings', icon: FiSettings, label: 'Settings' },
];

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { user, logout } = useAuth();
  const { isDark, toggleTheme } = useTheme();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <>
      {/* Mobile Toggle */}
      <button className="mobile-toggle" onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? <FiX size={24} /> : <FiMenu size={24} />}
      </button>

      {/* Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="sidebar-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        className={`sidebar ${isOpen ? 'open' : ''}`}
        initial={false}
      >
        {/* Logo */}
        <div className="sidebar-logo">
          <div className="logo-icon">
            <FiDroplet size={28} />
          </div>
          <span className="logo-text">AquaGuard</span>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => 
                `nav-item ${isActive ? 'active' : ''}`
              }
              onClick={() => setIsOpen(false)}
            >
              <item.icon size={20} />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Bottom Section */}
        <div className="sidebar-footer">
          {/* Theme Toggle */}
          <button className="theme-toggle" onClick={toggleTheme}>
            {isDark ? <FiSun size={18} /> : <FiMoon size={18} />}
            <span>{isDark ? 'Light Mode' : 'Dark Mode'}</span>
          </button>

          {/* User Profile */}
          {user && (
            <div className="user-profile">
              <img 
                src={user.picture || `https://ui-avatars.com/api/?name=${user.name}&background=0ea5e9&color=fff`} 
                alt={user.name}
                className="user-avatar"
              />
              <div className="user-info">
                <span className="user-name">{user.name}</span>
                <span className="user-email">{user.email}</span>
              </div>
            </div>
          )}

          {/* Logout Button */}
          <button className="logout-btn" onClick={handleLogout}>
            <FiLogOut size={18} />
            <span>Logout</span>
          </button>
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;
