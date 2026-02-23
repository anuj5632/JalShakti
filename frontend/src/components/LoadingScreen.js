import React from 'react';
import { motion } from 'framer-motion';
import { FiDroplet } from 'react-icons/fi';
import './LoadingScreen.css';

const LoadingScreen = () => {
  return (
    <div className="loading-screen">
      <motion.div
        className="loading-content"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        <motion.div
          className="loading-icon"
          animate={{ 
            y: [0, -10, 0],
            rotate: [0, 5, -5, 0]
          }}
          transition={{ 
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
        >
          <FiDroplet size={48} />
        </motion.div>
        <h2 className="loading-title">AquaGuard</h2>
        <div className="loading-bar">
          <motion.div
            className="loading-bar-fill"
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        </div>
        <p className="loading-text">Loading your dashboard...</p>
      </motion.div>
    </div>
  );
};

export default LoadingScreen;
