import React from 'react';
import { motion } from 'framer-motion';
import { FiDroplet, FiShield, FiActivity, FiBell, FiPlay } from 'react-icons/fi';
import { FcGoogle } from 'react-icons/fc';
import { useAuth } from '../context/AuthContext';
import './LoginPage.css';

const features = [
  { icon: FiActivity, title: 'Real-time Monitoring', desc: 'Track pH, TDS, turbidity, and more' },
  { icon: FiShield, title: 'ML Anomaly Detection', desc: 'AI-powered quality alerts' },
  { icon: FiBell, title: 'Instant SMS Alerts', desc: 'Get notified immediately' },
];

const LoginPage = () => {
  const { login, demoLogin } = useAuth();

  return (
    <div className="login-page">
      {/* Left Panel - Branding */}
      <motion.div 
        className="login-branding"
        initial={{ opacity: 0, x: -50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="brand-content">
          <div className="brand-logo">
            <FiDroplet size={48} />
          </div>
          <h1 className="brand-title">AquaGuard</h1>
          <p className="brand-subtitle">IoT Water Quality Monitoring System</p>

          <div className="features-list">
            {features.map((feature, index) => (
              <motion.div 
                key={index}
                className="feature-item"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
              >
                <div className="feature-icon">
                  <feature.icon size={24} />
                </div>
                <div className="feature-text">
                  <h3>{feature.title}</h3>
                  <p>{feature.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Water Animation */}
        <div className="water-animation">
          <div className="wave wave1"></div>
          <div className="wave wave2"></div>
          <div className="wave wave3"></div>
        </div>
      </motion.div>

      {/* Right Panel - Login Form */}
      <motion.div 
        className="login-form-panel"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="login-form-content">
          <h2 className="login-title">Welcome</h2>
          <p className="login-subtitle">Sign in to access your water quality dashboard</p>

          {/* Demo Button - Primary for easy testing */}
          <button 
            className="demo-login-btn"
            onClick={demoLogin}
          >
            <FiPlay size={22} />
            <span>Try Demo (Recommended)</span>
          </button>

          <div className="login-divider">
            <span>or</span>
          </div>

          {/* Google Login */}
          <button className="google-login-btn" onClick={login}>
            <FcGoogle size={22} />
            <span>Continue with Google</span>
          </button>

          <p className="login-note">
            Demo mode lets you explore all features without signing in.
            Your data is stored locally in your browser.
          </p>

          <p className="login-terms">
            By signing in, you agree to our Terms of Service and Privacy Policy
          </p>
        </div>

        <div className="login-footer">
          <p>Built for NSS Hackathon 2024</p>
          <p className="team-credit">Team AquaGuard</p>
        </div>
      </motion.div>
    </div>
  );
};

export default LoginPage;
