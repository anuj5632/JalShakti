import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiDroplet, FiPlus, FiEdit2, FiTrash2, FiMoreVertical,
  FiActivity, FiMapPin, FiClock, FiX
} from 'react-icons/fi';
import toast from 'react-hot-toast';
import { sourcesAPI } from '../services/api';
import './SourcesPage.css';

const sourceTypes = [
  { value: 'overhead_tank', label: 'Overhead Tank', icon: '🏠' },
  { value: 'storage_tank', label: 'Storage Tank', icon: '🛢️' },
  { value: 'kitchen_tap', label: 'Kitchen Tap', icon: '🚰' },
  { value: 'bathroom_tap', label: 'Bathroom Tap', icon: '🚿' },
  { value: 'garden_tap', label: 'Garden Tap', icon: '🌱' },
  { value: 'borewell', label: 'Borewell', icon: '💧' },
];

// Mock sources data
const initialSources = [
  {
    id: '1',
    name: 'Main Overhead Tank',
    source_type: 'overhead_tank',
    location: 'Rooftop',
    capacity_liters: 1000,
    is_active: true,
    quality_score: 85,
    last_reading: {
      ph: 7.2,
      tds: 220,
      turbidity: 2.1,
      water_level: 72
    },
    updated_at: new Date().toISOString()
  },
  {
    id: '2',
    name: 'Kitchen Tap',
    source_type: 'kitchen_tap',
    location: 'Kitchen',
    is_active: true,
    quality_score: 78,
    last_reading: {
      ph: 7.0,
      tds: 280,
      turbidity: 2.8,
      flow_rate: 4.5
    },
    updated_at: new Date().toISOString()
  },
];

const SourcesPage = () => {
  const [sources, setSources] = useState(initialSources);
  const [showModal, setShowModal] = useState(false);
  const [editingSource, setEditingSource] = useState(null);
  const [loading, setLoading] = useState(true);
  const [apiConnected, setApiConnected] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    source_type: 'overhead_tank',
    location: '',
    capacity_liters: '',
    description: ''
  });

  // Fetch sources from API
  const fetchSources = useCallback(async () => {
    try {
      const response = await sourcesAPI.getAll();
      if (response.data?.sources) {
        setSources(response.data.sources);
        setApiConnected(true);
      }
    } catch (error) {
      console.warn('API unavailable, using local data');
      setApiConnected(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingSource) {
        // Update existing source
        if (apiConnected) {
          await sourcesAPI.update(editingSource.id, formData);
        }
        setSources(prev => prev.map(s => 
          s.id === editingSource.id 
            ? { ...s, ...formData, updated_at: new Date().toISOString() }
            : s
        ));
        toast.success('Source updated successfully!');
      } else {
        // Create new source
        if (apiConnected) {
          const response = await sourcesAPI.create(formData);
          if (response.data?.data) {
            setSources(prev => [...prev, response.data.data]);
            toast.success('Source added successfully!');
            closeModal();
            return;
          }
        }
        // Fallback to local state
        const newSource = {
          id: Date.now().toString(),
          ...formData,
          is_active: true,
          quality_score: 0,
          last_reading: null,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        setSources(prev => [...prev, newSource]);
        toast.success('Source added successfully!');
      }
    } catch (error) {
      console.error('Failed to save source:', error);
      toast.error('Failed to save source');
    }
    
    closeModal();
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this source?')) {
      try {
        if (apiConnected) {
          await sourcesAPI.delete(id);
        }
        setSources(prev => prev.filter(s => s.id !== id));
        toast.success('Source deleted');
      } catch (error) {
        console.error('Failed to delete source:', error);
        toast.error('Failed to delete source');
      }
    }
  };

  const openModal = (source = null) => {
    if (source) {
      setEditingSource(source);
      setFormData({
        name: source.name,
        source_type: source.source_type,
        location: source.location || '',
        capacity_liters: source.capacity_liters || '',
        description: source.description || ''
      });
    } else {
      setEditingSource(null);
      setFormData({
        name: '',
        source_type: 'overhead_tank',
        location: '',
        capacity_liters: '',
        description: ''
      });
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setEditingSource(null);
  };

  const getSourceIcon = (type) => {
    const found = sourceTypes.find(s => s.value === type);
    return found?.icon || '💧';
  };

  const getQualityColor = (score) => {
    if (score >= 80) return 'var(--success)';
    if (score >= 60) return 'var(--warning)';
    return 'var(--danger)';
  };

  return (
    <div className="sources-page">
      <div className="page-header">
        <div>
          <h1>Water Sources</h1>
          <p>Manage your water monitoring points</p>
        </div>
        <button className="btn btn-primary" onClick={() => openModal()}>
          <FiPlus /> Add Source
        </button>
      </div>

      {/* Sources Grid */}
      <div className="sources-grid">
        {sources.map((source, index) => (
          <motion.div
            key={source.id}
            className="source-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <div className="source-header">
              <div className="source-icon">{getSourceIcon(source.source_type)}</div>
              <div className="source-actions">
                <button onClick={() => openModal(source)}><FiEdit2 /></button>
                <button onClick={() => handleDelete(source.id)}><FiTrash2 /></button>
              </div>
            </div>

            <h3 className="source-name">{source.name}</h3>
            <p className="source-type">{sourceTypes.find(s => s.value === source.source_type)?.label}</p>

            {source.location && (
              <div className="source-meta">
                <FiMapPin size={14} />
                <span>{source.location}</span>
              </div>
            )}

            <div className="source-quality">
              <span className="quality-label">Quality Score</span>
              <div className="quality-bar">
                <div 
                  className="quality-fill" 
                  style={{ 
                    width: `${source.quality_score}%`,
                    background: getQualityColor(source.quality_score)
                  }}
                />
              </div>
              <span className="quality-value" style={{ color: getQualityColor(source.quality_score) }}>
                {source.quality_score}%
              </span>
            </div>

            {source.last_reading && (
              <div className="source-readings">
                {source.last_reading.ph && (
                  <div className="reading">
                    <span>pH</span>
                    <strong>{source.last_reading.ph}</strong>
                  </div>
                )}
                {source.last_reading.tds && (
                  <div className="reading">
                    <span>TDS</span>
                    <strong>{source.last_reading.tds}</strong>
                  </div>
                )}
                {source.last_reading.water_level && (
                  <div className="reading">
                    <span>Level</span>
                    <strong>{source.last_reading.water_level}%</strong>
                  </div>
                )}
              </div>
            )}

            <div className="source-footer">
              <span className={`status-badge ${source.is_active ? 'active' : 'inactive'}`}>
                {source.is_active ? 'Online' : 'Offline'}
              </span>
              <span className="last-updated">
                <FiClock size={12} />
                Just now
              </span>
            </div>
          </motion.div>
        ))}

        {/* Add Source Card */}
        <motion.div
          className="source-card add-card"
          onClick={() => openModal()}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <FiPlus size={40} />
          <span>Add New Source</span>
        </motion.div>
      </div>

      {/* Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div 
            className="modal-overlay"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeModal}
          >
            <motion.div 
              className="modal"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={e => e.stopPropagation()}
            >
              <div className="modal-header">
                <h2>{editingSource ? 'Edit Source' : 'Add New Source'}</h2>
                <button className="close-btn" onClick={closeModal}><FiX /></button>
              </div>

              <form onSubmit={handleSubmit}>
                <div className="form-group">
                  <label className="form-label">Source Name</label>
                  <input
                    type="text"
                    className="form-input"
                    value={formData.name}
                    onChange={e => setFormData({...formData, name: e.target.value})}
                    placeholder="e.g., Main Overhead Tank"
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Source Type</label>
                  <select
                    className="form-input form-select"
                    value={formData.source_type}
                    onChange={e => setFormData({...formData, source_type: e.target.value})}
                  >
                    {sourceTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.icon} {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Location</label>
                    <input
                      type="text"
                      className="form-input"
                      value={formData.location}
                      onChange={e => setFormData({...formData, location: e.target.value})}
                      placeholder="e.g., Rooftop"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Capacity (Liters)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={formData.capacity_liters}
                      onChange={e => setFormData({...formData, capacity_liters: e.target.value})}
                      placeholder="e.g., 1000"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Description (Optional)</label>
                  <textarea
                    className="form-input"
                    value={formData.description}
                    onChange={e => setFormData({...formData, description: e.target.value})}
                    placeholder="Add any notes about this source..."
                    rows={3}
                  />
                </div>

                <div className="modal-actions">
                  <button type="button" className="btn btn-secondary" onClick={closeModal}>
                    Cancel
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingSource ? 'Update Source' : 'Add Source'}
                  </button>
                </div>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SourcesPage;
