import { useState, useEffect } from 'react';
import Modal from './Modal';
import { api } from '../api';

export default function ResponseFormModal({ isOpen, onClose, response, endpointId, onSuccess }) {
  const [formData, setFormData] = useState({
    endpoint: endpointId,
    name: '',
    description: '',
    response_status: 200,
    content_type: 'application/json',
    response_body: '{"message": "Success"}',
    custom_headers: {},
    is_default: false,
    position: 0,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (response) {
      setFormData(response);
    } else {
      setFormData({
        endpoint: endpointId,
        name: '',
        description: '',
        response_status: 200,
        content_type: 'application/json',
        response_body: '{"message": "Success"}',
        custom_headers: {},
        is_default: false,
        position: 0,
      });
    }
    setError('');
  }, [response, endpointId, isOpen]);

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
      if (response) {
        await api.updateResponse(response.id, formData);
      } else {
        await api.createResponse(formData);
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
      title={response ? 'Edit Response' : 'New Response'}
    >
      <form onSubmit={handleSubmit} className="form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Response Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="Success Response"
            required
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Response description"
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
            rows={8}
            className="code-input"
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group-checkbox">
            <input
              type="checkbox"
              name="is_default"
              checked={formData.is_default}
              onChange={handleChange}
              id="is_default_response"
            />
            <label htmlFor="is_default_response">Set as Default Response</label>
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

        <div className="form-actions">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Saving...' : response ? 'Update' : 'Create'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
