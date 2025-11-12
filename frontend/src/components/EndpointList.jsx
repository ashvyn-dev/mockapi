import { useState } from 'react';
import EndpointFormModal from './EndpointFormModal';
import DeleteConfirmModal from './DeleteConfirmModal';
import { api } from '../api';

const methodColors = {
  GET: '#10b981',
  POST: '#3b82f6',
  PUT: '#f59e0b',
  PATCH: '#8b5cf6',
  DELETE: '#ef4444',
  OPTIONS: '#6b7280',
};

export default function EndpointList({
  collection,
  endpoints,
  selectedEndpoint,
  onSelectEndpoint,
  onRefresh
}) {
  const [showEndpointForm, setShowEndpointForm] = useState(false);
  const [editingEndpoint, setEditingEndpoint] = useState(null);
  const [deletingEndpoint, setDeletingEndpoint] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [endpointsExpanded, setEndpointsExpanded] = useState(true);

  const handleEdit = (e, endpoint) => {
    e.stopPropagation();
    setEditingEndpoint(endpoint);
    setShowEndpointForm(true);
  };

  const handleDelete = (e, endpoint) => {
    e.stopPropagation();
    setDeletingEndpoint(endpoint);
  };

  const confirmDelete = async () => {
    setDeleteLoading(true);
    try {
      await api.deleteEndpoint(deletingEndpoint.id);
      setDeletingEndpoint(null);
      onRefresh();
    } catch (error) {
      console.error('Failed to delete endpoint:', error);
      alert('Failed to delete endpoint');
    } finally {
      setDeleteLoading(false);
    }
  };

  if (!collection) {
    return (
      <div className="endpoint-list empty">
        <p>Select a collection to view endpoints</p>
      </div>
    );
  }

  return (
    <>
      <div className="endpoint-list">
        <div className="list-header">
          <div>
            <h2>{collection.name}</h2>
            <span className="endpoint-count">{endpoints.length} endpoints</span>
          </div>
          <button
            className="btn-primary-small"
            onClick={() => {
              setEditingEndpoint(null);
              setShowEndpointForm(true);
            }}
          >
            + New Endpoint
          </button>
        </div>

        <div className="endpoints-header">
          <div
            className="section-title-clickable"
            onClick={() => setEndpointsExpanded(!endpointsExpanded)}
          >
            <span className="collapse-icon">{endpointsExpanded ? '▼' : '▶'}</span>
            <span className="section-title">Endpoints</span>
          </div>
        </div>

        {endpointsExpanded && (
          <>
            {endpoints.length === 0 ? (
              <div className="empty-state">
                <p>No endpoints in this collection</p>
                <button
                  className="btn-primary"
                  onClick={() => {
                    setEditingEndpoint(null);
                    setShowEndpointForm(true);
                  }}
                >
                  Create First Endpoint
                </button>
              </div>
            ) : (
              <div className="endpoints">
                {endpoints.map((endpoint) => (
                  <div
                    key={endpoint.id}
                    className={`endpoint-item ${
                      selectedEndpoint?.id === endpoint.id ? 'active' : ''
                    }`}
                    onClick={() => onSelectEndpoint(endpoint)}
                  >
                    <span
                      className="method-badge"
                      style={{ backgroundColor: methodColors[endpoint.http_method] }}
                    >
                      {endpoint.http_method}
                    </span>
                    <div className="endpoint-info">
                      <div className="endpoint-name">{endpoint.display_name}</div>
                      <div className="endpoint-path">/{endpoint.path}</div>
                    </div>
                    <div className="endpoint-actions">
                      <button
                        className="action-btn-small"
                        onClick={(e) => handleEdit(e, endpoint)}
                        title="Edit"
                      >
                        ✏️
                      </button>
                      <button
                        className="action-btn-small"
                        onClick={(e) => handleDelete(e, endpoint)}
                        title="Delete"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      <EndpointFormModal
        isOpen={showEndpointForm}
        onClose={() => {
          setShowEndpointForm(false);
          setEditingEndpoint(null);
        }}
        endpoint={editingEndpoint}
        collectionId={collection.id}
        onSuccess={onRefresh}
      />

      <DeleteConfirmModal
        isOpen={!!deletingEndpoint}
        onClose={() => setDeletingEndpoint(null)}
        onConfirm={confirmDelete}
        itemName={deletingEndpoint?.display_name}
        loading={deleteLoading}
      />
    </>
  );
}
