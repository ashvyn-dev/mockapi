import { useState, useEffect } from 'react';
import Modal from './Modal';
import { api } from '../api';

export default function CollectionFormModal({ isOpen, onClose, collection, onSuccess }) {
  const [formData, setFormData] = useState({
    slug: '',
    name: '',
    description: '',
    is_active: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (collection) {
      setFormData({
        slug: collection.slug,
        name: collection.name,
        description: collection.description || '',
        is_active: collection.is_active,
      });
    } else {
      setFormData({
        slug: '',
        name: '',
        description: '',
        is_active: true,
      });
    }
    setError('');
  }, [collection, isOpen]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (collection) {
        await api.updateCollection(collection.slug, formData);
      } else {
        await api.createCollection(formData);
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
      title={collection ? 'Edit Collection' : 'New Collection'}
    >
      <form onSubmit={handleSubmit} className="form">
        {error && <div className="error-message">{error}</div>}

        <div className="form-group">
          <label>Slug *</label>
          <input
            type="text"
            name="slug"
            value={formData.slug}
            onChange={handleChange}
            placeholder="my-collection"
            required
            disabled={!!collection}
          />
          <small>URL-safe identifier (cannot be changed after creation)</small>
        </div>

        <div className="form-group">
          <label>Name *</label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            placeholder="My Collection"
            required
          />
        </div>

        <div className="form-group">
          <label>Description</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            placeholder="Collection description"
            rows={3}
          />
        </div>

        <div className="form-group-checkbox">
          <input
            type="checkbox"
            name="is_active"
            checked={formData.is_active}
            onChange={handleChange}
            id="is_active"
          />
          <label htmlFor="is_active">Active</label>
        </div>

        <div className="form-actions">
          <button type="button" onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button type="submit" disabled={loading} className="btn-primary">
            {loading ? 'Saving...' : collection ? 'Update' : 'Create'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
