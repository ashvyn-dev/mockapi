import { useState, useEffect } from 'react';
import Modal from './Modal';
import { api } from '../api';

export default function EndpointFormModal({ isOpen, onClose, endpoint, collectionId, onSuccess }) {
  const [formData, setFormData] = useState({
    collection: collectionId,
    display_name: '',
    description: '',
    path: '',
    http_method: 'GET',
    response_status: 200,
    content_type: 'application/json',
    content_encoding: '',
    response_body: '{"message": "Success"}',
    custom_headers: {},
    enable_dynamic_response: false,
    enable_request_logger: true,
    response_delay: 0,
    position: 0,
    is_active: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (endpoint) {
      setFormData({
        collection: endpoint.collection,
        display_name: endpoint.display_name,
        description: endpoint.description || '',
        path: endpoint.path,
        http_method: endpoint.http_method,
        response_status: endpoint.response_status,
        content_type: endpoint.content_type,
        content_encoding: endpoint.content_encoding || '',
        response_body: endpoint.response_body,
        custom_headers: endpoint.custom_headers || {},
        enable_dynamic_response: endpoint.enable_dynamic_response,
        enable_request_logger: endpoint.enable_request_logger,
        response_delay: endpoint.response_delay,
        position: endpoint.position,
        is_active: endpoint.is_active,
      });
    } else {
      setFormData({
        collection: collectionId,
        display_name: '',
        description: '',
        path: '',
        http_method: 'GET',
        response_status: 200,
        content_type: 'application/json',
        content_encoding: '',
        response_body: '{"message": "Success"}',
        custom_headers: {},
        enable_dynamic_response: false,
        enable_request_logger: true,
        response_delay: 0,
        position: 0,
        is_active: true,
      });
    }
    setError('');
  }, [endpoint, collectionId, isOpen]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (endpoint) {
        await api.updateEndpoint(endpoint.id, formData);
      } else {
        await api.createEndpoint(formData);
      }
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.response?.data?.detail || 'Operation failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={endpoint ? 'Edit Endpoint' : 'New Endpoint'}
    >
      <form onSubmit={handleSubmit} className="form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-row">
          <div className="form-group">
            <label>Display Name *</label>
            <input
              type="text"
              name="display_name"
              value={formData.display_name}
              onChange={handleChange}
              placeholder="Get Users"
              required
            />
          </div>

          <div className="form-group">
            <label>HTTP Method *</label>
            <select name="http_method" value={formData.http_method} onChange={handleChange}>
              <option value="GET">GET</option>
              <option value="POST">POST</option>
              <option value="PUT">PUT</option>
              <option value="PATCH">PATCH</option>
              <option value="DELETE">DELETE</option>
              <option value="OPTIONS">OPTIONS</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Path *</label>
          <input
            type="text"
            name="path"
            value={formData.path}
            onChange={handleChange}
            placeholder="users"
            required
          />
          <small>Path after collection (e.g., "users" or "users/123")</small>
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Endpoint description"
            rows={2}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Response Status *</label>
            <select name="response_status" value={formData.response_status} onChange={handleChange}>
              <option value={200}>200 - OK</option>
              <option value={201}>201 - Created</option>
              <option value={204}>204 - No Content</option>
              <option value={400}>400 - Bad Request</option>
              <option value={401}>401 - Unauthorized</option>
              <option value={403}>403 - Forbidden</option>
              <option value={404}>404 - Not Found</option>
              <option value={500}>500 - Internal Server Error</option>
            </select>
          </div>

          <div className="form-group">
            <label>Content Type *</label>
            <select name="content_type" value={formData.content_type} onChange={handleChange}>
              <option value="application/json">application/json</option>
              <option value="application/xml">application/xml</option>
              <option value="text/plain">text/plain</option>
              <option value="text/html">text/html</option>
            </select>
          </div>
        </div>

        <div className="form-group">
          <label>Response Body *</label>
          <textarea
            name="response_body"
            value={formData.response_body}
            onChange={handleChange}
            placeholder='{"message": "Success"}'
            rows={6}
            className="code-input"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Response Delay (seconds)</label>
            <input
              type="number"
              name="response_delay"
              value={formData.response_delay}
              onChange={handleChange}
              min="0"
            />
          </div>

          <div className="form-group">
            <label>Position</label>
            <input
              type="number"
              name="position"
              value={formData.position}
              onChange={handleChange}
              min="0"
            />
          </div>
        </div>

        <div className="form-checkboxes">
          <div className="form-group-checkbox">
            <input
              type="checkbox"
              name="enable_request_logger"
              checked={formData.enable_request_logger}
              onChange={handleChange}
              id="enable_request_logger"
            />
            <label htmlFor="enable_request_logger">Enable Request Logger</label>
          </div>

          <div className="form-group-checkbox">
            <input
              type="checkbox"
              name="is_active"
              checked={formData.is_active}
              onChange={handleChange}
              id="is_active_endpoint"
            />
            <label htmlFor="is_active_endpoint">Active</label>
          </div>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Saving...' : endpoint ? 'Update' : 'Create'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
