import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FiAlertCircle, FiAlertTriangle, FiInfo, FiCheck, 
  FiClock, FiFilter, FiX 
} from 'react-icons/fi';
import './AlertsPage.css';

const mockAlerts = [
  {
    id: 1,
    title: 'High TDS Level Detected',
    message: 'TDS reading of 580 mg/L exceeds the safe limit of 500 mg/L in Kitchen Tap',
    severity: 'critical',
    source: 'Kitchen Tap',
    metric: 'TDS',
    value: 580,
    threshold: 500,
    status: 'active',
    created_at: new Date(Date.now() - 30 * 60000).toISOString(),
  },
  {
    id: 2,
    title: 'Water Level Low',
    message: 'Overhead tank water level has dropped below 20%',
    severity: 'warning',
    source: 'Main Overhead Tank',
    metric: 'Water Level',
    value: 18,
    threshold: 20,
    status: 'active',
    created_at: new Date(Date.now() - 2 * 3600000).toISOString(),
  },
  {
    id: 3,
    title: 'pH Level Normalized',
    message: 'pH level has returned to normal range after previous alert',
    severity: 'info',
    source: 'Kitchen Tap',
    metric: 'pH',
    value: 7.2,
    threshold: 8.5,
    status: 'resolved',
    created_at: new Date(Date.now() - 5 * 3600000).toISOString(),
    resolved_at: new Date(Date.now() - 4 * 3600000).toISOString(),
  },
  {
    id: 4,
    title: 'Flow Rate Anomaly',
    message: 'Unusual flow pattern detected - possible leak or blockage',
    severity: 'warning',
    source: 'Bathroom Tap',
    metric: 'Flow Rate',
    value: 0.3,
    threshold: 0.5,
    status: 'acknowledged',
    created_at: new Date(Date.now() - 8 * 3600000).toISOString(),
    acknowledged_at: new Date(Date.now() - 7 * 3600000).toISOString(),
  },
];

const AlertsPage = () => {
  const [alerts, setAlerts] = useState(mockAlerts);
  const [filter, setFilter] = useState('all');

  const filteredAlerts = alerts.filter(alert => {
    if (filter === 'all') return true;
    return alert.status === filter;
  });

  const handleAcknowledge = (id) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === id 
        ? { ...alert, status: 'acknowledged', acknowledged_at: new Date().toISOString() }
        : alert
    ));
  };

  const handleResolve = (id) => {
    setAlerts(prev => prev.map(alert => 
      alert.id === id 
        ? { ...alert, status: 'resolved', resolved_at: new Date().toISOString() }
        : alert
    ));
  };

  const handleDismiss = (id) => {
    setAlerts(prev => prev.filter(alert => alert.id !== id));
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical': return <FiAlertCircle />;
      case 'warning': return <FiAlertTriangle />;
      default: return <FiInfo />;
    }
  };

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} hours ago`;
    return date.toLocaleDateString();
  };

  const activeCount = alerts.filter(a => a.status === 'active').length;

  return (
    <div className="alerts-page">
      <div className="page-header">
        <div>
          <h1>Alerts</h1>
          <p>{activeCount} active alerts requiring attention</p>
        </div>
      </div>

      {/* Filters */}
      <div className="filters">
        {['all', 'active', 'acknowledged', 'resolved'].map(f => (
          <button
            key={f}
            className={`filter-btn ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            {f === 'active' && activeCount > 0 && (
              <span className="filter-count">{activeCount}</span>
            )}
          </button>
        ))}
      </div>

      {/* Alerts List */}
      <div className="alerts-list">
        {filteredAlerts.length === 0 ? (
          <div className="empty-state">
            <FiCheck size={48} />
            <h3>No alerts</h3>
            <p>All clear! No {filter !== 'all' ? filter : ''} alerts at the moment.</p>
          </div>
        ) : (
          filteredAlerts.map((alert, index) => (
            <motion.div
              key={alert.id}
              className={`alert-card ${alert.severity} ${alert.status}`}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <div className="alert-icon">
                {getSeverityIcon(alert.severity)}
              </div>

              <div className="alert-body">
                <div className="alert-header">
                  <h3>{alert.title}</h3>
                  <span className={`severity-badge ${alert.severity}`}>
                    {alert.severity}
                  </span>
                </div>

                <p className="alert-message">{alert.message}</p>

                <div className="alert-meta">
                  <span className="meta-item">
                    <FiClock size={14} />
                    {formatTime(alert.created_at)}
                  </span>
                  <span className="meta-item">
                    Source: <strong>{alert.source}</strong>
                  </span>
                  <span className="meta-item">
                    {alert.metric}: <strong>{alert.value}</strong> (limit: {alert.threshold})
                  </span>
                </div>

                {alert.status !== 'resolved' && (
                  <div className="alert-actions">
                    {alert.status === 'active' && (
                      <button 
                        className="btn btn-secondary"
                        onClick={() => handleAcknowledge(alert.id)}
                      >
                        Acknowledge
                      </button>
                    )}
                    <button 
                      className="btn btn-primary"
                      onClick={() => handleResolve(alert.id)}
                    >
                      <FiCheck /> Mark Resolved
                    </button>
                  </div>
                )}

                {alert.status === 'resolved' && (
                  <div className="resolved-info">
                    <FiCheck /> Resolved {formatTime(alert.resolved_at)}
                  </div>
                )}
              </div>

              <button 
                className="dismiss-btn"
                onClick={() => handleDismiss(alert.id)}
              >
                <FiX />
              </button>
            </motion.div>
          ))
        )}
      </div>
    </div>
  );
};

export default AlertsPage;
