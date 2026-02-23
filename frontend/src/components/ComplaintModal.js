import React, { useState } from 'react';
import axios from 'axios';
import './ComplaintModal.css';

const ComplaintModal = ({ isOpen, onClose, sensorData, qualityScore, userEmail }) => {
  const [language, setLanguage] = useState('english');
  const [location, setLocation] = useState('Main Water Tank');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [showHistory, setShowHistory] = useState(false);

  const languageOptions = [
    { value: 'english', label: 'English', flag: '🇬🇧' },
    { value: 'hindi', label: 'हिंदी', flag: '🇮🇳' },
    { value: 'marathi', label: 'मराठी', flag: '🇮🇳' }
  ];

  const texts = {
    english: {
      title: '📋 File Government Complaint',
      subtitle: 'Report poor water quality to authorities',
      location: 'Location',
      language: 'Complaint Language',
      currentReadings: 'Current Readings',
      qualityScore: 'Quality Score',
      submit: 'File Complaint Now',
      submitting: 'Filing Complaint...',
      success: 'Complaint Filed Successfully!',
      trackingId: 'Tracking ID',
      department: 'Filed with',
      helpline: 'Helpline',
      history: 'View Complaint History',
      noComplaints: 'No complaints filed yet',
      close: 'Close'
    },
    hindi: {
      title: '📋 सरकारी शिकायत दर्ज करें',
      subtitle: 'खराब पानी की गुणवत्ता की रिपोर्ट करें',
      location: 'स्थान',
      language: 'शिकायत भाषा',
      currentReadings: 'वर्तमान रीडिंग',
      qualityScore: 'गुणवत्ता स्कोर',
      submit: 'अभी शिकायत दर्ज करें',
      submitting: 'शिकायत दर्ज हो रही है...',
      success: 'शिकायत सफलतापूर्वक दर्ज!',
      trackingId: 'ट्रैकिंग आईडी',
      department: 'दर्ज किया गया',
      helpline: 'हेल्पलाइन',
      history: 'शिकायत इतिहास देखें',
      noComplaints: 'अभी तक कोई शिकायत दर्ज नहीं',
      close: 'बंद करें'
    },
    marathi: {
      title: '📋 सरकारी तक्रार नोंदवा',
      subtitle: 'खराब पाण्याच्या गुणवत्तेची तक्रार करा',
      location: 'ठिकाण',
      language: 'तक्रार भाषा',
      currentReadings: 'सध्याचे रीडिंग',
      qualityScore: 'गुणवत्ता स्कोअर',
      submit: 'आता तक्रार नोंदवा',
      submitting: 'तक्रार नोंदवली जात आहे...',
      success: 'तक्रार यशस्वीरित्या नोंदवली!',
      trackingId: 'ट्रॅकिंग आयडी',
      department: 'नोंदणी केली',
      helpline: 'हेल्पलाइन',
      history: 'तक्रार इतिहास पहा',
      noComplaints: 'अद्याप कोणतीही तक्रार नोंदवलेली नाही',
      close: 'बंद करा'
    }
  };

  const t = texts[language];

  const fileComplaint = async () => {
    setIsSubmitting(true);
    setResult(null);

    try {
      const params = new URLSearchParams({
        location: location,
        quality_score: qualityScore,
        ph: sensorData?.ph || 7.0,
        tds: sensorData?.tds || 250,
        turbidity: sensorData?.turbidity || 2.5,
        temperature: sensorData?.temperature || 26,
        water_level: sensorData?.waterLevel || 75,
        flow_rate: sensorData?.flowRate || 5,
        language: language,
        user_email: userEmail || ''
      });

      const response = await axios.post(`http://localhost:8000/api/v1/file-complaint?${params.toString()}`);
      
      if (response.data.success) {
        setResult(response.data);
      } else {
        throw new Error(response.data.error || 'Failed to file complaint');
      }
    } catch (error) {
      console.error('Failed to file complaint:', error);
      setResult({ error: error.message });
    } finally {
      setIsSubmitting(false);
    }
  };

  const fetchComplaintHistory = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/v1/my-complaints');
      if (response.data.success) {
        setComplaints(response.data.complaints);
        setShowHistory(true);
      }
    } catch (error) {
      console.error('Failed to fetch complaints:', error);
    }
  };

  const getStatusColor = (score) => {
    if (score < 50) return '#ef4444';
    if (score < 70) return '#f59e0b';
    return '#10b981';
  };

  if (!isOpen) return null;

  return (
    <div className="complaint-modal-overlay" onClick={onClose}>
      <div className="complaint-modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close-btn" onClick={onClose}>×</button>
        
        <div className="complaint-header">
          <h2>{t.title}</h2>
          <p>{t.subtitle}</p>
        </div>

        {!result ? (
          <>
            <div className="complaint-form">
              <div className="form-group">
                <label>{t.location}</label>
                <input
                  type="text"
                  value={location}
                  onChange={(e) => setLocation(e.target.value)}
                  placeholder="Enter your location"
                />
              </div>

              <div className="form-group">
                <label>{t.language}</label>
                <div className="language-buttons">
                  {languageOptions.map(opt => (
                    <button
                      key={opt.value}
                      className={`lang-option ${language === opt.value ? 'active' : ''}`}
                      onClick={() => setLanguage(opt.value)}
                    >
                      <span className="flag">{opt.flag}</span>
                      <span>{opt.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              <div className="current-readings">
                <h4>{t.currentReadings}</h4>
                <div className="readings-grid">
                  <div className="reading-item">
                    <span className="reading-label">pH</span>
                    <span className="reading-value">{sensorData?.ph?.toFixed(1) || 'N/A'}</span>
                  </div>
                  <div className="reading-item">
                    <span className="reading-label">TDS</span>
                    <span className="reading-value">{sensorData?.tds?.toFixed(0) || 'N/A'} ppm</span>
                  </div>
                  <div className="reading-item">
                    <span className="reading-label">Turbidity</span>
                    <span className="reading-value">{sensorData?.turbidity?.toFixed(1) || 'N/A'} NTU</span>
                  </div>
                  <div className="reading-item quality-score-item">
                    <span className="reading-label">{t.qualityScore}</span>
                    <span 
                      className="reading-value score"
                      style={{ color: getStatusColor(qualityScore) }}
                    >
                      {qualityScore?.toFixed(1) || 'N/A'}%
                    </span>
                  </div>
                </div>
              </div>

              <button 
                className="submit-complaint-btn"
                onClick={fileComplaint}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <span className="spinner"></span>
                    {t.submitting}
                  </>
                ) : (
                  <>
                    <span className="btn-icon">📤</span>
                    {t.submit}
                  </>
                )}
              </button>
            </div>

            <button className="history-btn" onClick={fetchComplaintHistory}>
              📜 {t.history}
            </button>

            {showHistory && (
              <div className="complaint-history">
                <h4>Complaint History</h4>
                {complaints.length === 0 ? (
                  <p className="no-complaints">{t.noComplaints}</p>
                ) : (
                  <div className="complaints-list">
                    {complaints.map((complaint, index) => (
                      <div key={index} className="complaint-item">
                        <div className="complaint-id">{complaint.complaint_id}</div>
                        <div className="complaint-dept">{complaint.department?.name}</div>
                        <div className="complaint-status">{complaint.status}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        ) : result.error ? (
          <div className="complaint-error">
            <span className="error-icon">❌</span>
            <p>{result.error}</p>
            <button onClick={() => setResult(null)}>Try Again</button>
          </div>
        ) : (
          <div className="complaint-success">
            <div className="success-animation">
              <span className="success-icon">✅</span>
            </div>
            <h3>{t.success}</h3>
            
            <div className="success-details">
              <div className="detail-row">
                <span className="detail-label">{t.trackingId}:</span>
                <span className="detail-value tracking-id">{result.complaint_id}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">{t.department}:</span>
                <span className="detail-value">{result.department}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">{t.helpline}:</span>
                <span className="detail-value phone">{result.helpline}</span>
              </div>
            </div>

            <p className="success-message">{result.message}</p>

            <button className="close-success-btn" onClick={onClose}>
              {t.close}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default ComplaintModal;
