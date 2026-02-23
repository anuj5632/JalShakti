import React, { useState, useEffect, useCallback, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  FiDroplet, FiActivity, FiThermometer, FiAlertCircle, 
  FiTrendingUp, FiTrendingDown, FiRefreshCw, FiCpu, FiZap,
  FiVolume2, FiVolumeX, FiBell
} from 'react-icons/fi';
import { 
  LineChart, Line, AreaChart, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar
} from 'recharts';
import { useAuth } from '../context/AuthContext';
import { dashboardAPI, alertsAPI } from '../services/api';
import axios from 'axios';
import alarmSound, { checkAndPlayAlarm } from '../utils/alarmSound';
import './Dashboard.css';

// Mock data generator
const generateMockData = () => {
  const now = new Date();
  return {
    ph: 6.8 + Math.random() * 1.4,
    tds: 180 + Math.random() * 140,
    turbidity: 1.5 + Math.random() * 2.5,
    flowRate: 3 + Math.random() * 4,
    waterLevel: 45 + Math.random() * 40,
    temperature: 24 + Math.random() * 4,
    timestamp: now.toISOString()
  };
};

const generateHistory = (count = 24) => {
  const history = [];
  const now = new Date();
  for (let i = count - 1; i >= 0; i--) {
    const time = new Date(now - i * 60 * 60 * 1000);
    history.push({
      time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      ph: (6.8 + Math.random() * 1.4).toFixed(2),
      tds: Math.round(180 + Math.random() * 140),
      turbidity: (1.5 + Math.random() * 2.5).toFixed(2),
      quality: Math.round(70 + Math.random() * 25)
    });
  }
  return history;
};

const MetricCard = ({ title, value, unit, icon: Icon, trend, status, color }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'excellent': return 'var(--success)';
      case 'good': return '#22d3ee';
      case 'fair': return 'var(--warning)';
      case 'poor': return '#f97316';
      case 'critical': return 'var(--danger)';
      default: return 'var(--accent-primary)';
    }
  };

  return (
    <motion.div 
      className="metric-card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
    >
      <div className="metric-header">
        <div className="metric-icon" style={{ background: `${color}20`, color }}>
          <Icon size={20} />
        </div>
        <span className={`metric-trend ${trend > 0 ? 'up' : 'down'}`}>
          {trend > 0 ? <FiTrendingUp /> : <FiTrendingDown />}
          {Math.abs(trend).toFixed(1)}%
        </span>
      </div>
      <div className="metric-value">
        {typeof value === 'number' ? value.toFixed(1) : value}
        <span className="metric-unit">{unit}</span>
      </div>
      <div className="metric-title">{title}</div>
      <div className="metric-status">
        <span className="status-dot" style={{ background: getStatusColor() }}></span>
        <span style={{ color: getStatusColor(), textTransform: 'capitalize' }}>{status}</span>
      </div>
    </motion.div>
  );
};

const QualityGauge = ({ score }) => {
  const getCategory = () => {
    if (score >= 90) return { label: 'Excellent', color: 'var(--success)' };
    if (score >= 75) return { label: 'Good', color: '#22d3ee' };
    if (score >= 50) return { label: 'Fair', color: 'var(--warning)' };
    if (score >= 25) return { label: 'Poor', color: '#f97316' };
    return { label: 'Critical', color: 'var(--danger)' };
  };

  const { label, color } = getCategory();
  const circumference = 2 * Math.PI * 80;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="quality-gauge">
      <svg viewBox="0 0 200 200" className="gauge-svg">
        <circle
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke="var(--bg-tertiary)"
          strokeWidth="12"
        />
        <motion.circle
          cx="100"
          cy="100"
          r="80"
          fill="none"
          stroke={color}
          strokeWidth="12"
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1, ease: "easeOut" }}
          transform="rotate(-90 100 100)"
        />
      </svg>
      <div className="gauge-content">
        <div className="gauge-score" style={{ color }}>{Math.round(score)}</div>
        <div className="gauge-label">{label}</div>
      </div>
    </div>
  );
};

const Dashboard = () => {
  const { user } = useAuth();
  const [data, setData] = useState(generateMockData());
  const [history, setHistory] = useState(generateHistory());
  const [qualityScore, setQualityScore] = useState(82);
  const [alerts, setAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);
  const [predictions, setPredictions] = useState(null);
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [alarmEnabled, setAlarmEnabled] = useState(true);
  const [currentAlarmStatus, setCurrentAlarmStatus] = useState('normal');
  const lastAlarmTime = useRef(0);

  // Check for critical values and play alarm
  useEffect(() => {
    if (!alarmEnabled) return;
    
    // Debounce: don't alarm more than once every 30 seconds
    const now = Date.now();
    if (now - lastAlarmTime.current < 30000) return;

    const status = checkAndPlayAlarm(data);
    setCurrentAlarmStatus(status);
    
    if (status !== 'normal') {
      lastAlarmTime.current = now;
    }
  }, [data, alarmEnabled]);

  const toggleAlarm = () => {
    setAlarmEnabled(!alarmEnabled);
    if (alarmEnabled) {
      alarmSound.stop();
    }
  };

  // Fetch ML predictions
  const fetchPredictions = useCallback(async () => {
    setLoadingPredictions(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/predict?device_id=demo&steps=5');
      if (response.data && response.data.predictions) {
        setPredictions(response.data.predictions);
      }
    } catch (error) {
      console.warn('Predictions API unavailable, using mock predictions');
      // Generate mock predictions based on current data
      setPredictions({
        ph: [data.ph, data.ph + 0.1, data.ph - 0.05, data.ph + 0.08, data.ph - 0.02].map(v => parseFloat(v.toFixed(2))),
        turbidity: [data.turbidity, data.turbidity + 0.3, data.turbidity + 0.5, data.turbidity + 0.2, data.turbidity + 0.4].map(v => parseFloat(v.toFixed(1))),
        tds: [data.tds, data.tds + 5, data.tds + 8, data.tds + 3, data.tds + 6].map(v => Math.round(v)),
        prediction_intervals: ['+5 min', '+10 min', '+15 min', '+20 min', '+25 min']
      });
    } finally {
      setLoadingPredictions(false);
    }
  }, [data]);

  // Fetch data from API or use mock
  const fetchDashboardData = useCallback(async () => {
    try {
      const response = await dashboardAPI.getSummary();
      if (response.data) {
        setApiConnected(true);
        const summary = response.data;
        if (summary.latest_reading) {
          setData(summary.latest_reading);
        }
        if (summary.overall_quality) {
          setQualityScore(summary.overall_quality);
        }
        // Fetch alerts
        const alertsResponse = await alertsAPI.getAll({ limit: 5 });
        if (alertsResponse.data?.alerts) {
          setAlerts(alertsResponse.data.alerts);
        }
      }
    } catch (error) {
      console.warn('API unavailable, using mock data');
      setApiConnected(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
    fetchPredictions();
  }, [fetchDashboardData, fetchPredictions]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      if (!apiConnected) {
        const newData = generateMockData();
        setData(newData);
        setQualityScore(70 + Math.random() * 25);
      } else {
        fetchDashboardData();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [apiConnected, fetchDashboardData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchDashboardData();
      if (!apiConnected) {
        setData(generateMockData());
        setHistory(generateHistory());
        setQualityScore(70 + Math.random() * 25);
      }
    } finally {
      setRefreshing(false);
    }
  };

  const getStatus = (metric, value) => {
    switch (metric) {
      case 'ph':
        if (value >= 6.5 && value <= 7.5) return 'excellent';
        if (value >= 6.0 && value <= 8.0) return 'good';
        if (value >= 5.5 && value <= 8.5) return 'fair';
        return 'poor';
      case 'tds':
        if (value <= 250) return 'excellent';
        if (value <= 350) return 'good';
        if (value <= 500) return 'fair';
        return 'poor';
      case 'turbidity':
        if (value <= 2) return 'excellent';
        if (value <= 4) return 'good';
        if (value <= 5) return 'fair';
        return 'poor';
      default:
        return 'good';
    }
  };

  const mockAlerts = alerts.length > 0 ? alerts.map(a => ({
    id: a.id || a.alert_id,
    type: a.severity || 'warning',
    message: a.message,
    time: a.created_at ? new Date(a.created_at).toLocaleString() : 'Just now'
  })) : [
    { id: 1, type: 'warning', message: 'TDS levels slightly elevated in Kitchen Tap', time: '2 hours ago' },
    { id: 2, type: 'info', message: 'Scheduled maintenance reminder for overhead tank', time: '5 hours ago' },
  ];

  return (
    <div className="dashboard">
      {/* Critical Alert Banner */}
      {currentAlarmStatus === 'critical' && (
        <motion.div 
          className="critical-alert-banner"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <FiBell className="alert-bell" />
          <span>CRITICAL: Water quality parameters exceeded safe limits!</span>
          <button onClick={() => setCurrentAlarmStatus('acknowledged')} className="dismiss-btn">
            Acknowledge
          </button>
        </motion.div>
      )}

      {/* Header */}
      <div className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>Welcome back, {user?.name?.split(' ')[0] || 'User'}! Here's your water quality overview.</p>
        </div>
        <div className="header-actions">
          <button 
            className={`btn btn-icon alarm-toggle ${alarmEnabled ? 'enabled' : 'disabled'}`}
            onClick={toggleAlarm}
            title={alarmEnabled ? 'Mute Alarms' : 'Enable Alarms'}
          >
            {alarmEnabled ? <FiVolume2 /> : <FiVolumeX />}
          </button>
          <button 
            className={`btn btn-secondary refresh-btn ${refreshing ? 'spinning' : ''}`}
            onClick={handleRefresh}
          >
            <FiRefreshCw />
            Refresh
          </button>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="metrics-grid">
        <MetricCard
          title="pH Level"
          value={data.ph}
          unit=""
          icon={FiDroplet}
          trend={2.3}
          status={getStatus('ph', data.ph)}
          color="#8b5cf6"
        />
        <MetricCard
          title="TDS"
          value={data.tds}
          unit="mg/L"
          icon={FiActivity}
          trend={-1.5}
          status={getStatus('tds', data.tds)}
          color="#0ea5e9"
        />
        <MetricCard
          title="Turbidity"
          value={data.turbidity}
          unit="NTU"
          icon={FiDroplet}
          trend={0.8}
          status={getStatus('turbidity', data.turbidity)}
          color="#22c55e"
        />
        <MetricCard
          title="Temperature"
          value={data.temperature}
          unit="°C"
          icon={FiThermometer}
          trend={1.2}
          status="good"
          color="#f59e0b"
        />
      </div>

      {/* Main Content Grid */}
      <div className="dashboard-content">
        {/* Quality Score */}
        <motion.div 
          className="card quality-card"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <h3>Water Quality Score</h3>
          <QualityGauge score={qualityScore} />
          <p className="quality-description">
            Your water quality is within safe drinking standards
          </p>
        </motion.div>

        {/* Chart */}
        <motion.div 
          className="card chart-card"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <h3>24-Hour Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={history}>
              <defs>
                <linearGradient id="colorQuality" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={12} />
              <YAxis stroke="var(--text-muted)" fontSize={12} />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px'
                }}
              />
              <Area
                type="monotone"
                dataKey="quality"
                stroke="#0ea5e9"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorQuality)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Alerts */}
        <motion.div 
          className="card alerts-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3>Recent Alerts</h3>
          <div className="alerts-list">
            {mockAlerts.map(alert => (
              <div key={alert.id} className={`alert-item ${alert.type}`}>
                <FiAlertCircle className="alert-icon" />
                <div className="alert-content">
                  <p>{alert.message}</p>
                  <span className="alert-time">{alert.time}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Water Level */}
        <motion.div 
          className="card level-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h3>Tank Water Level</h3>
          <div className="tank-visual">
            <div className="tank">
              <motion.div 
                className="water-fill"
                initial={{ height: 0 }}
                animate={{ height: `${data.waterLevel}%` }}
                transition={{ duration: 1, ease: "easeOut" }}
              />
              <div className="level-markers">
                {[100, 75, 50, 25, 0].map(level => (
                  <div key={level} className="marker">
                    <span>{level}%</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="level-info">
              <span className="level-value">{Math.round(data.waterLevel)}%</span>
              <span className="level-label">Current Level</span>
            </div>
          </div>
        </motion.div>

        {/* ML Predictions */}
        <motion.div 
          className="card predictions-card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="predictions-header">
            <h3><FiCpu /> ML Predictions</h3>
            <button 
              className="btn-small"
              onClick={fetchPredictions}
              disabled={loadingPredictions}
            >
              {loadingPredictions ? 'Loading...' : 'Refresh'}
            </button>
          </div>
          {predictions ? (
            <div className="predictions-content">
              <div className="prediction-chart">
                <ResponsiveContainer width="100%" height={180}>
                  <LineChart data={predictions.prediction_intervals?.map((interval, i) => ({
                    time: interval,
                    ph: predictions.ph[i],
                    turbidity: predictions.turbidity[i],
                    tds: predictions.tds[i] / 10 // Scale down for chart
                  }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
                    <XAxis dataKey="time" stroke="var(--text-muted)" fontSize={10} />
                    <YAxis stroke="var(--text-muted)" fontSize={10} />
                    <Tooltip
                      contentStyle={{
                        background: 'var(--bg-secondary)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '8px'
                      }}
                      formatter={(value, name) => [
                        name === 'tds' ? (value * 10).toFixed(0) + ' ppm' : value.toFixed(2),
                        name.toUpperCase()
                      ]}
                    />
                    <Line type="monotone" dataKey="ph" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} />
                    <Line type="monotone" dataKey="turbidity" stroke="#22c55e" strokeWidth={2} dot={{ r: 3 }} />
                    <Line type="monotone" dataKey="tds" stroke="#0ea5e9" strokeWidth={2} dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="prediction-values">
                <div className="pred-item">
                  <span className="pred-label">pH in 25min</span>
                  <span className="pred-value" style={{ color: '#8b5cf6' }}>
                    {predictions.ph[4]?.toFixed(2)}
                  </span>
                </div>
                <div className="pred-item">
                  <span className="pred-label">Turbidity</span>
                  <span className="pred-value" style={{ color: '#22c55e' }}>
                    {predictions.turbidity[4]?.toFixed(1)} NTU
                  </span>
                </div>
                <div className="pred-item">
                  <span className="pred-label">TDS</span>
                  <span className="pred-value" style={{ color: '#0ea5e9' }}>
                    {predictions.tds[4]} ppm
                  </span>
                </div>
              </div>
              <p className="prediction-note">
                <FiZap size={12} /> Powered by Scikit-Learn ML Model
              </p>
            </div>
          ) : (
            <div className="predictions-loading">
              <p>Loading predictions...</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
