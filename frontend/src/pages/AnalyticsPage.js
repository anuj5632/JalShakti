import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  FiCalendar, FiTrendingUp, FiDroplet, FiActivity 
} from 'react-icons/fi';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import './AnalyticsPage.css';

// Generate mock analytics data
const generateDailyData = (days = 7) => {
  const data = [];
  const today = new Date();
  
  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    
    data.push({
      date: date.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }),
      ph: (6.8 + Math.random() * 0.8).toFixed(2),
      tds: Math.round(200 + Math.random() * 150),
      turbidity: (1.5 + Math.random() * 2).toFixed(2),
      quality: Math.round(70 + Math.random() * 25)
    });
  }
  
  return data;
};

const qualityDistribution = [
  { name: 'Excellent', value: 45, color: '#22c55e' },
  { name: 'Good', value: 30, color: '#0ea5e9' },
  { name: 'Fair', value: 15, color: '#f59e0b' },
  { name: 'Poor', value: 10, color: '#ef4444' }
];

const sourceComparison = [
  { name: 'Overhead Tank', ph: 7.2, tds: 220, turbidity: 2.1, quality: 85 },
  { name: 'Kitchen Tap', ph: 7.0, tds: 280, turbidity: 2.8, quality: 78 },
  { name: 'Storage Tank', ph: 7.1, tds: 240, turbidity: 2.3, quality: 82 },
];

const AnalyticsPage = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [dailyData] = useState(generateDailyData(timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 14));

  const stats = [
    { label: 'Avg. pH', value: '7.1', change: '+0.1', icon: FiDroplet, color: '#8b5cf6' },
    { label: 'Avg. TDS', value: '245', unit: 'mg/L', change: '-12', icon: FiActivity, color: '#0ea5e9' },
    { label: 'Avg. Quality', value: '81%', change: '+3%', icon: FiTrendingUp, color: '#22c55e' },
    { label: 'Anomalies', value: '3', change: '-2', icon: FiActivity, color: '#f59e0b' },
  ];

  return (
    <div className="analytics-page">
      <div className="page-header">
        <div>
          <h1>Analytics</h1>
          <p>Water quality trends and insights</p>
        </div>
        <div className="time-selector">
          {['7d', '14d', '30d'].map(range => (
            <button
              key={range}
              className={`time-btn ${timeRange === range ? 'active' : ''}`}
              onClick={() => setTimeRange(range)}
            >
              {range === '7d' ? '7 Days' : range === '14d' ? '14 Days' : '30 Days'}
            </button>
          ))}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="stats-grid">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            className="stat-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <div className="stat-icon" style={{ background: `${stat.color}20`, color: stat.color }}>
              <stat.icon size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-label">{stat.label}</span>
              <div className="stat-value">
                {stat.value}
                {stat.unit && <span className="stat-unit">{stat.unit}</span>}
              </div>
              <span className={`stat-change ${stat.change.startsWith('+') ? 'positive' : 'negative'}`}>
                {stat.change} from last period
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Quality Trend */}
        <motion.div 
          className="card chart-card large"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h3>Quality Score Trend</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={dailyData}>
              <defs>
                <linearGradient id="qualityGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} />
              <YAxis stroke="var(--text-muted)" fontSize={12} domain={[0, 100]} />
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
                fill="url(#qualityGradient)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Quality Distribution */}
        <motion.div 
          className="card chart-card"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <h3>Quality Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={qualityDistribution}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={4}
                dataKey="value"
              >
                {qualityDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>

        {/* pH & TDS Trend */}
        <motion.div 
          className="card chart-card"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <h3>pH & TDS Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="date" stroke="var(--text-muted)" fontSize={12} />
              <YAxis yAxisId="left" stroke="var(--text-muted)" fontSize={12} />
              <YAxis yAxisId="right" orientation="right" stroke="var(--text-muted)" fontSize={12} />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="ph" stroke="#8b5cf6" strokeWidth={2} dot={false} />
              <Line yAxisId="right" type="monotone" dataKey="tds" stroke="#0ea5e9" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Source Comparison */}
        <motion.div 
          className="card chart-card large"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h3>Source Comparison</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sourceComparison}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
              <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} />
              <YAxis stroke="var(--text-muted)" fontSize={12} />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-secondary)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '8px'
                }}
              />
              <Legend />
              <Bar dataKey="quality" fill="#0ea5e9" radius={[4, 4, 0, 0]} />
              <Bar dataKey="tds" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
