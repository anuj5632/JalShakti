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

// Realistic sensor simulation - gradual changes like real sensors
let currentSensorValues = {
  ph: 7.2,
  tds: 245,
  turbidity: 2.1,
  flowRate: 5.2,
  waterLevel: 72,
  temperature: 26.5
};

// Calculate quality score based on actual sensor readings (WHO standards)
const calculateQualityScore = (ph, tds, turbidity) => {
  // pH scoring (ideal: 6.5-8.5, optimal: 7.0-7.5)
  let phScore = 100;
  if (ph < 6.5 || ph > 8.5) phScore = 20;
  else if (ph < 6.8 || ph > 8.2) phScore = 50;
  else if (ph < 7.0 || ph > 7.5) phScore = 75;
  else phScore = 100;

  // TDS scoring (ideal: <300 ppm, acceptable: <500 ppm)
  let tdsScore = 100;
  if (tds > 500) tdsScore = 20;
  else if (tds > 400) tdsScore = 50;
  else if (tds > 300) tdsScore = 75;
  else if (tds > 200) tdsScore = 90;
  else tdsScore = 100;

  // Turbidity scoring (ideal: <1 NTU, acceptable: <5 NTU)
  let turbidityScore = 100;
  if (turbidity > 5) turbidityScore = 20;
  else if (turbidity > 4) turbidityScore = 50;
  else if (turbidity > 3) turbidityScore = 70;
  else if (turbidity > 2) turbidityScore = 85;
  else if (turbidity > 1) turbidityScore = 95;
  else turbidityScore = 100;

  // Weighted average (turbidity most important for drinking water)
  return Math.round(phScore * 0.3 + tdsScore * 0.3 + turbidityScore * 0.4);
};

// Get individual scores for display
const getIndividualScores = (ph, tds, turbidity) => {
  let phScore = 100;
  if (ph < 6.5 || ph > 8.5) phScore = 20;
  else if (ph < 6.8 || ph > 8.2) phScore = 50;
  else if (ph < 7.0 || ph > 7.5) phScore = 75;
  else phScore = 100;

  let tdsScore = 100;
  if (tds > 500) tdsScore = 20;
  else if (tds > 400) tdsScore = 50;
  else if (tds > 300) tdsScore = 75;
  else if (tds > 200) tdsScore = 90;
  else tdsScore = 100;

  let turbidityScore = 100;
  if (turbidity > 5) turbidityScore = 20;
  else if (turbidity > 4) turbidityScore = 50;
  else if (turbidity > 3) turbidityScore = 70;
  else if (turbidity > 2) turbidityScore = 85;
  else if (turbidity > 1) turbidityScore = 95;
  else turbidityScore = 100;

  return { phScore, tdsScore, turbidityScore };
};

// Simulate gradual sensor drift (like real sensors)
const generateRealisticData = () => {
  const now = new Date();
  
  // Small random drift (-0.02 to +0.02 for pH, etc.)
  currentSensorValues.ph += (Math.random() - 0.5) * 0.04;
  currentSensorValues.tds += (Math.random() - 0.5) * 4;
  currentSensorValues.turbidity += (Math.random() - 0.5) * 0.08;
  currentSensorValues.flowRate += (Math.random() - 0.5) * 0.2;
  currentSensorValues.waterLevel += (Math.random() - 0.5) * 0.5;
  currentSensorValues.temperature += (Math.random() - 0.5) * 0.1;

  // Keep values in realistic bounds
  currentSensorValues.ph = Math.max(6.0, Math.min(9.0, currentSensorValues.ph));
  currentSensorValues.tds = Math.max(100, Math.min(600, currentSensorValues.tds));
  currentSensorValues.turbidity = Math.max(0.5, Math.min(6, currentSensorValues.turbidity));
  currentSensorValues.flowRate = Math.max(2, Math.min(8, currentSensorValues.flowRate));
  currentSensorValues.waterLevel = Math.max(30, Math.min(95, currentSensorValues.waterLevel));
  currentSensorValues.temperature = Math.max(20, Math.min(32, currentSensorValues.temperature));

  return {
    ph: parseFloat(currentSensorValues.ph.toFixed(2)),
    tds: Math.round(currentSensorValues.tds),
    turbidity: parseFloat(currentSensorValues.turbidity.toFixed(2)),
    flowRate: parseFloat(currentSensorValues.flowRate.toFixed(1)),
    waterLevel: parseFloat(currentSensorValues.waterLevel.toFixed(1)),
    temperature: parseFloat(currentSensorValues.temperature.toFixed(1)),
    timestamp: now.toISOString()
  };
};

// Simulate contamination event (for demo - gradual degradation)
let contaminationActive = false;
let contaminationStartTime = null;

const simulateContamination = () => {
  // Gradually increase turbidity and TDS (contamination effect)
  currentSensorValues.turbidity += 0.15;
  currentSensorValues.tds += 8;
  currentSensorValues.ph += (Math.random() - 0.5) * 0.1;
};

const generateHistory = (count = 24) => {
  const history = [];
  const now = new Date();
  // Start with good values and simulate gradual changes
  let histPh = 7.1;
  let histTds = 230;
  let histTurb = 1.8;
  
  for (let i = count - 1; i >= 0; i--) {
    const time = new Date(now - i * 60 * 60 * 1000);
    // Small gradual changes
    histPh += (Math.random() - 0.5) * 0.1;
    histTds += (Math.random() - 0.5) * 10;
    histTurb += (Math.random() - 0.5) * 0.2;
    
    // Keep in bounds
    histPh = Math.max(6.5, Math.min(8.0, histPh));
    histTds = Math.max(180, Math.min(350, histTds));
    histTurb = Math.max(1.0, Math.min(4.0, histTurb));
    
    const quality = calculateQualityScore(histPh, histTds, histTurb);
    
    history.push({
      time: time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
      ph: histPh.toFixed(2),
      tds: Math.round(histTds),
      turbidity: histTurb.toFixed(2),
      quality: quality
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
  const [data, setData] = useState(generateRealisticData());
  const [history, setHistory] = useState(generateHistory());
  const [qualityScore, setQualityScore] = useState(() => {
    const initial = generateRealisticData();
    return calculateQualityScore(initial.ph, initial.tds, initial.turbidity);
  });
  const [alerts, setAlerts] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [apiConnected, setApiConnected] = useState(false);
  const [predictions, setPredictions] = useState(null);
  const [loadingPredictions, setLoadingPredictions] = useState(false);
  const [alarmEnabled, setAlarmEnabled] = useState(true);
  const [currentAlarmStatus, setCurrentAlarmStatus] = useState('normal');
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [demoMode, setDemoMode] = useState(null); // 'normal', 'warning', 'critical'
  const [emailAlertsEnabled, setEmailAlertsEnabled] = useState(localStorage.getItem('emailAlertsEnabled') !== 'false');
  const [emailSending, setEmailSending] = useState(false);
  const [lastEmailSent, setLastEmailSent] = useState(null);
  const lastAlarmTime = useRef(0);
  const lastEmailTime = useRef(0);

  // Get user's registered email
  const userEmail = user?.email;

  // Function to send email alert to registered user email
  const sendEmailAlert = async (alertType, sensorData, score) => {
    if (!userEmail) {
      console.log('No user email found - not logged in');
      return;
    }
    
    if (!emailAlertsEnabled) {
      console.log('Email alerts disabled by user');
      return;
    }
    
    // Don't send more than one email per 30 seconds (for demo)
    const now = Date.now();
    if (now - lastEmailTime.current < 30000) {
      console.log('Email cooldown active, skipping...');
      return;
    }
    
    setEmailSending(true);
    console.log('Sending email to registered user:', userEmail);
    
    try {
      const response = await axios.post('http://localhost:8000/api/v1/send-alert-email', null, {
        params: {
          recipients: userEmail,
          alert_type: alertType,
          location: 'Main Water Tank',
          ph: sensorData.ph,
          tds: sensorData.tds,
          turbidity: sensorData.turbidity,
          temperature: sensorData.temperature,
          water_level: sensorData.waterLevel,
          flow_rate: sensorData.flowRate,
          quality_score: score
        }
      });
      
      console.log('Email API response:', response.data);
      
      if (response.data.success) {
        lastEmailTime.current = now;
        setLastEmailSent(new Date());
        console.log('Alert email sent successfully to:', userEmail);
      } else {
        console.error('Email send failed:', response.data);
      }
    } catch (error) {
      console.error('Failed to send email alert:', error);
    } finally {
      setEmailSending(false);
    }
  };

  // Toggle email alerts
  const toggleEmailAlerts = () => {
    const newState = !emailAlertsEnabled;
    setEmailAlertsEnabled(newState);
    localStorage.setItem('emailAlertsEnabled', newState.toString());
  };

  // Manual test email function
  const sendTestEmail = async () => {
    if (!userEmail) {
      alert('Please login with Google to receive email alerts!');
      return;
    }
    
    setEmailSending(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/test-email', null, {
        params: { recipient: userEmail }
      });
      
      if (response.data.success) {
        setLastEmailSent(new Date());
        alert('Test email sent to ' + userEmail + '! Check your inbox.');
      } else {
        alert('Failed to send email: ' + (response.data.message || response.data.error));
      }
    } catch (error) {
      console.error('Test email failed:', error);
      alert('Failed to send test email. Check console for details.');
    } finally {
      setEmailSending(false);
    }
  };

  // Check for critical values and play alarm
  useEffect(() => {
    if (!alarmEnabled) return;
    
    // Debounce: don't alarm more than once every 30 seconds
    const now = Date.now();
    if (now - lastAlarmTime.current < 30000) return;

    // Trigger alarm if quality score drops below 70%
    if (qualityScore < 70) {
      if (qualityScore < 50) {
        // Critical - below 50%
        alarmSound.playCriticalAlarm(4000);
        setCurrentAlarmStatus('critical');
        // Send critical email alert
        sendEmailAlert('critical', data, qualityScore);
      } else {
        // Warning - below 70%
        alarmSound.playWarningAlarm(2000);
        setCurrentAlarmStatus('warning');
        // Send warning email alert
        sendEmailAlert('warning', data, qualityScore);
      }
      lastAlarmTime.current = now;
    } else {
      setCurrentAlarmStatus('normal');
    }

    // Also check individual sensor values
    const status = checkAndPlayAlarm(data);
    if (status !== 'normal' && now - lastAlarmTime.current >= 30000) {
      setCurrentAlarmStatus(status);
      lastAlarmTime.current = now;
    }
  }, [data, qualityScore, alarmEnabled]);

  const toggleAlarm = () => {
    setAlarmEnabled(!alarmEnabled);
    if (alarmEnabled) {
      alarmSound.stop();
    }
  };

  // Demo scenarios for presentation
  const triggerDemoScenario = (scenario) => {
    setDemoMode(scenario);
    switch(scenario) {
      case 'normal':
        // Good water quality
        currentSensorValues.ph = 7.2;
        currentSensorValues.tds = 220;
        currentSensorValues.turbidity = 1.5;
        contaminationActive = false;
        break;
      case 'warning':
        // Medium contamination - triggers warning alarm
        currentSensorValues.ph = 7.8;
        currentSensorValues.tds = 380;
        currentSensorValues.turbidity = 3.8;
        contaminationActive = false;
        break;
      case 'critical':
        // Severe contamination - triggers critical alarm
        currentSensorValues.ph = 8.6;
        currentSensorValues.tds = 520;
        currentSensorValues.turbidity = 5.5;
        contaminationActive = false;
        break;
      case 'gradual':
        // Start gradual contamination
        currentSensorValues.ph = 7.2;
        currentSensorValues.tds = 245;
        currentSensorValues.turbidity = 2.1;
        contaminationActive = true;
        contaminationStartTime = Date.now();
        break;
      default:
        break;
    }
    // Force immediate update
    const newData = generateRealisticData();
    setData(newData);
    setQualityScore(calculateQualityScore(newData.ph, newData.tds, newData.turbidity));
    setLastUpdate(new Date());
  };

  // Keyboard shortcuts for demo
  useEffect(() => {
    const handleKeyPress = (e) => {
      if (e.key === '1') triggerDemoScenario('normal');
      if (e.key === '2') triggerDemoScenario('warning');
      if (e.key === '3') triggerDemoScenario('critical');
      if (e.key === '4') triggerDemoScenario('gradual');
    };
    window.addEventListener('keypress', handleKeyPress);
    return () => window.removeEventListener('keypress', handleKeyPress);
  }, []);

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

  // Simulate real-time updates with realistic sensor behavior
  useEffect(() => {
    const interval = setInterval(() => {
      if (!apiConnected) {
        // If contamination is active, simulate degradation
        if (contaminationActive) {
          simulateContamination();
          // Auto-stop after 2 minutes
          if (Date.now() - contaminationStartTime > 120000) {
            contaminationActive = false;
          }
        }
        
        const newData = generateRealisticData();
        setData(newData);
        setLastUpdate(new Date());
        
        // Calculate quality based on actual sensor values
        const calculatedQuality = calculateQualityScore(newData.ph, newData.tds, newData.turbidity);
        setQualityScore(calculatedQuality);
        
        // Update history with new data point
        setHistory(prev => {
          const newHistory = [...prev.slice(1), {
            time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
            ph: newData.ph.toFixed(2),
            tds: newData.tds,
            turbidity: newData.turbidity.toFixed(2),
            quality: calculatedQuality
          }];
          return newHistory;
        });
      } else {
        fetchDashboardData();
      }
    }, 3000); // Update every 3 seconds for smoother real-time feel

    return () => clearInterval(interval);
  }, [apiConnected, fetchDashboardData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchDashboardData();
      if (!apiConnected) {
        const newData = generateRealisticData();
        setData(newData);
        setHistory(generateHistory());
        setQualityScore(calculateQualityScore(newData.ph, newData.tds, newData.turbidity));
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
          <span>CRITICAL: Water quality dropped below 50%! Immediate attention required!</span>
          <button onClick={() => setCurrentAlarmStatus('acknowledged')} className="dismiss-btn">
            Acknowledge
          </button>
        </motion.div>
      )}

      {/* Warning Alert Banner */}
      {currentAlarmStatus === 'warning' && (
        <motion.div 
          className="warning-alert-banner"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <FiBell className="alert-bell" />
          <span>WARNING: Water quality below 70% - Check your water sources</span>
          <button onClick={() => setCurrentAlarmStatus('acknowledged')} className="dismiss-btn">
            Dismiss
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
          <div className="connection-status">
            <span className={`status-indicator ${apiConnected ? 'connected' : 'simulation'}`}></span>
            <span className="status-text">{apiConnected ? 'Live Sensors' : 'Simulation Mode'}</span>
          </div>
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
          <div className="quality-header">
            <h3>Water Quality Score</h3>
            <div className="last-update">
              <span className="update-label">Last Check:</span>
              <span className="update-time">{lastUpdate.toLocaleString('en-IN', { 
                day: '2-digit', 
                month: 'short', 
                year: 'numeric',
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
              })}</span>
            </div>
          </div>
          <QualityGauge score={qualityScore} />
          
          {/* Quality Score Breakdown */}
          <div className="quality-breakdown">
            <h4>Score Breakdown (WHO Standards)</h4>
            <div className="breakdown-items">
              <div className="breakdown-item">
                <div className="breakdown-label">
                  <span>pH Level</span>
                  <span className="breakdown-value">{data.ph?.toFixed(2)}</span>
                </div>
                <div className="breakdown-bar">
                  <div 
                    className="breakdown-fill" 
                    style={{ 
                      width: `${getIndividualScores(data.ph, data.tds, data.turbidity).phScore}%`,
                      background: getIndividualScores(data.ph, data.tds, data.turbidity).phScore >= 75 ? 'var(--success)' : getIndividualScores(data.ph, data.tds, data.turbidity).phScore >= 50 ? 'var(--warning)' : 'var(--danger)'
                    }}
                  ></div>
                </div>
                <span className="breakdown-score">{getIndividualScores(data.ph, data.tds, data.turbidity).phScore}%</span>
              </div>
              <div className="breakdown-item">
                <div className="breakdown-label">
                  <span>TDS</span>
                  <span className="breakdown-value">{data.tds} ppm</span>
                </div>
                <div className="breakdown-bar">
                  <div 
                    className="breakdown-fill" 
                    style={{ 
                      width: `${getIndividualScores(data.ph, data.tds, data.turbidity).tdsScore}%`,
                      background: getIndividualScores(data.ph, data.tds, data.turbidity).tdsScore >= 75 ? 'var(--success)' : getIndividualScores(data.ph, data.tds, data.turbidity).tdsScore >= 50 ? 'var(--warning)' : 'var(--danger)'
                    }}
                  ></div>
                </div>
                <span className="breakdown-score">{getIndividualScores(data.ph, data.tds, data.turbidity).tdsScore}%</span>
              </div>
              <div className="breakdown-item">
                <div className="breakdown-label">
                  <span>Turbidity</span>
                  <span className="breakdown-value">{data.turbidity?.toFixed(2)} NTU</span>
                </div>
                <div className="breakdown-bar">
                  <div 
                    className="breakdown-fill" 
                    style={{ 
                      width: `${getIndividualScores(data.ph, data.tds, data.turbidity).turbidityScore}%`,
                      background: getIndividualScores(data.ph, data.tds, data.turbidity).turbidityScore >= 75 ? 'var(--success)' : getIndividualScores(data.ph, data.tds, data.turbidity).turbidityScore >= 50 ? 'var(--warning)' : 'var(--danger)'
                    }}
                  ></div>
                </div>
                <span className="breakdown-score">{getIndividualScores(data.ph, data.tds, data.turbidity).turbidityScore}%</span>
              </div>
            </div>
            <div className="weight-info">
              <small>Weights: pH (30%) + TDS (30%) + Turbidity (40%) = Overall Score</small>
            </div>
          </div>

          {/* Email Alert Settings */}
          <div className="email-alert-settings">
            <h4>📧 Email Alerts</h4>
            {userEmail ? (
              <>
                <div className="registered-email">
                  <span className="email-label">Registered Email:</span>
                  <span className="user-email">{userEmail}</span>
                </div>
                <div className="email-controls">
                  <label className="toggle-label">
                    <input
                      type="checkbox"
                      checked={emailAlertsEnabled}
                      onChange={toggleEmailAlerts}
                    />
                    <span>Enable email alerts</span>
                  </label>
                  <button 
                    className="test-email-btn"
                    onClick={sendTestEmail}
                    disabled={emailSending}
                  >
                    {emailSending ? 'Sending...' : 'Test Email'}
                  </button>
                </div>
                {lastEmailSent && (
                  <span className="email-status sent">
                    Last sent: {lastEmailSent.toLocaleTimeString()}
                  </span>
                )}
                <p className="email-info">
                  {emailAlertsEnabled 
                    ? '✅ Alerts enabled - emails sent when quality < 70%' 
                    : '⏸️ Email alerts paused'}
                </p>
              </>
            ) : (
              <p className="email-info login-required">
                🔐 Please login with Google to receive email alerts
              </p>
            )}
          </div>

          {/* Demo Scenarios for Presentation */}
          <div className="demo-scenarios">
            <h4>Demo Scenarios</h4>
            <div className="scenario-buttons">
              <button 
                className={`scenario-btn normal ${demoMode === 'normal' ? 'active' : ''}`}
                onClick={() => triggerDemoScenario('normal')}
              >
                Normal (1)
              </button>
              <button 
                className={`scenario-btn warning ${demoMode === 'warning' ? 'active' : ''}`}
                onClick={() => triggerDemoScenario('warning')}
              >
                Warning (2)
              </button>
              <button 
                className={`scenario-btn critical ${demoMode === 'critical' ? 'active' : ''}`}
                onClick={() => triggerDemoScenario('critical')}
              >
                Critical (3)
              </button>
              <button 
                className={`scenario-btn gradual ${demoMode === 'gradual' ? 'active' : ''}`}
                onClick={() => triggerDemoScenario('gradual')}
              >
                Gradual (4)
              </button>
            </div>
          </div>
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
