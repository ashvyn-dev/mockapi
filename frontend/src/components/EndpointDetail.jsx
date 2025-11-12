import { useState, useEffect } from 'react';
import { api } from '../api';
import ResponseViewer from './ResponseViewer';
import ResponseFormModal from './ResponseFormModal';
import DeleteConfirmModal from './DeleteConfirmModal';

export default function EndpointDetail({ endpoint, collectionSlug, onRefresh }) {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState(endpoint);
  const [responses, setResponses] = useState([]);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [requestBody, setRequestBody] = useState('');
  const [customHeaders, setCustomHeaders] = useState('');

  const [showResponseForm, setShowResponseForm] = useState(false);
  const [editingResponse, setEditingResponse] = useState(null);
  const [deletingResponse, setDeletingResponse] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [responsesExpanded, setResponsesExpanded] = useState(true);

  useEffect(() => {
    setFormData(endpoint);
    setIsEditing(false);
    loadResponses();
  }, [endpoint]);

  const loadResponses = async () => {
    try {
      const data = await api.getResponses(endpoint.id);
      setResponses(data);
    } catch (error) {
      console.error('Failed to load responses:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : type === 'number' ? parseInt(value) : value,
    });
  };

  const handleSave = async () => {
    setSaveLoading(true);
    try {
      await api.updateEndpoint(endpoint.id, formData);
      setIsEditing(false);
      onRefresh();
    } catch (error) {
      console.error('Failed to update endpoint:', error);
      alert('Failed to update endpoint');
    } finally {
      setSaveLoading(false);
    }
  };

  const handleCancel = () => {
    setFormData(endpoint);
    setIsEditing(false);
  };

  const handleTest = async () => {
    setLoading(true);
    try {
      let body = undefined;
      if (['POST', 'PUT', 'PATCH'].includes(endpoint.http_method) && requestBody) {
        body = JSON.parse(requestBody);
      }

      let headers = {};
      if (customHeaders) {
        headers = JSON.parse(customHeaders);
      }

      const result = await api.testEndpoint(
        collectionSlug,
        endpoint.path,
        endpoint.http_method,
        body,
        headers
      );
      setResponse(result);
    } catch (error) {
      setResponse({
        status: 0,
        statusText: 'Error',
        headers: {},
        data: { error: error.message },
        time: 0,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteResponse = async () => {
    setDeleteLoading(true);
    try {
      await api.deleteResponse(deletingResponse.id);
      setDeletingResponse(null);
      loadResponses();
    } catch (error) {
      console.error('Failed to delete response:', error);
      alert('Failed to delete response');
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <>
      <div className="endpoint-detail">
        <div className="detail-header">
          <h3>{endpoint.display_name}</h3>
          <div className="detail-actions">
            {isEditing ? (
              <>
                <button className="btn-secondary" onClick={handleCancel}>
                  Cancel
                </button>
                <button
                  className="btn-primary"
                  onClick={handleSave}
                  disabled={saveLoading}
                >
                  {saveLoading ? 'Saving...' : 'Save Changes'}
                </button>
              </>
            ) : (
              <>
                <button className="btn-secondary" onClick={() => setIsEditing(true)}>
                  ✏️ Edit
                </button>
                <button
                  className="test-button"
                  onClick={handleTest}
                  disabled={loading}
                >
                  {loading ? 'Testing...' : '▶ Send Request'}
                </button>
              </>
            )}
          </div>
        </div>

        {isEditing ? (
          <div className="edit-form">
            <div className="detail-section">
              <div className="section-label">Basic Information</div>
              <div className="form-row">
                <div className="form-group">
                  <label>Display Name</label>
                  <input
                    type="text"
                    name="display_name"
                    value={formData.display_name}
                    onChange={handleChange}
                  />
                </div>
                <div className="form-group">
                  <label>HTTP Method</label>
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
                <label>Path</label>
                <input
                  type="text"
                  name="path"
                  value={formData.path}
                  onChange={handleChange}
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  name="description"
                  value={formData.description || ''}
                  onChange={handleChange}
                  rows={2}
                />
              </div>
            </div>

            <div className="detail-section">
              <div className="section-label">Default Response</div>
              <div className="form-row">
                <div className="form-group">
                  <label>Status Code</label>
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
                  <label>Content Type</label>
                  <select name="content_type" value={formData.content_type} onChange={handleChange}>
                    <option value="application/json">application/json</option>
                    <option value="application/xml">application/xml</option>
                    <option value="text/plain">text/plain</option>
                    <option value="text/html">text/html</option>
                  </select>
                </div>
              </div>
              <div className="form-group">
                <label>Response Body</label>
                <textarea
                  name="response_body"
                  value={formData.response_body}
                  onChange={handleChange}
                  rows={8}
                  className="code-editor"
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
                <div className="form-group-checkbox">
                  <input
                    type="checkbox"
                    name="enable_request_logger"
                    checked={formData.enable_request_logger}
                    onChange={handleChange}
                    id="logger_edit"
                  />
                  <label htmlFor="logger_edit">Enable Request Logger</label>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <>
            <div className="detail-section">
              <div className="section-label">Endpoint</div>
              <div className="endpoint-url">
                <span className="method">{endpoint.http_method}</span>
                <code>/{collectionSlug}/{endpoint.path}</code>
              </div>
              {endpoint.description && (
                <p className="endpoint-description">{endpoint.description}</p>
              )}
            </div>

            {['POST', 'PUT', 'PATCH'].includes(endpoint.http_method) && (
              <div className="detail-section">
                <div className="section-label">Request Body (JSON)</div>
                <textarea
                  className="code-editor"
                  value={requestBody}
                  onChange={(e) => setRequestBody(e.target.value)}
                  placeholder='{"key": "value"}'
                  rows={6}
                />
              </div>
            )}

            <div className="detail-section">
              <div className="section-label">Custom Headers (JSON)</div>
              <textarea
                className="code-editor"
                value={customHeaders}
                onChange={(e) => setCustomHeaders(e.target.value)}
                placeholder='{"Authorization": "Bearer token"}'
                rows={4}
              />
            </div>

            <div className="detail-section">
              <div className="section-label">Default Response</div>
              <div className="response-config">
                <div className="config-item">
                  <span className="config-label">Status:</span>
                  <span className="config-value">{endpoint.response_status}</span>
                </div>
                <div className="config-item">
                  <span className="config-label">Content-Type:</span>
                  <span className="config-value">{endpoint.content_type}</span>
                </div>
                {endpoint.response_delay > 0 && (
                  <div className="config-item">
                    <span className="config-label">Delay:</span>
                    <span className="config-value">{endpoint.response_delay}s</span>
                  </div>
                )}
              </div>
              <pre className="code-block">{endpoint.response_body}</pre>
            </div>

            <div className="detail-section">
              <div className="section-header">
                <div
                  className="section-title-clickable"
                  onClick={() => setResponsesExpanded(!responsesExpanded)}
                >
                  <span className="collapse-icon">{responsesExpanded ? '▼' : '▶'}</span>
                  <span className="section-label">Additional Responses ({responses.length})</span>
                </div>
                <button
                  className="btn-primary-small"
                  onClick={() => {
                    setEditingResponse(null);
                    setShowResponseForm(true);
                  }}
                >
                  + Add Response
                </button>
              </div>

              {responsesExpanded && (
                <>
                  {responses.length > 0 ? (
                    <div className="responses-list">
                      {responses.map((resp) => (
                        <div key={resp.id} className="response-card">
                          <div className="response-card-header">
                            <div>
                              <span className="response-name">{resp.name}</span>
                              {resp.is_default && <span className="default-badge">Default</span>}
                            </div>
                            <div className="response-card-actions">
                              <span className="status-badge-small" style={{
                                backgroundColor: resp.response_status < 300 ? '#10b981' : '#ef4444'
                              }}>
                                {resp.response_status}
                              </span>
                              <button
                                className="action-btn-small"
                                onClick={() => {
                                  setEditingResponse(resp);
                                  setShowResponseForm(true);
                                }}
                              >
                                ✏️
                              </button>
                              <button
                                className="action-btn-small"
                                onClick={() => setDeletingResponse(resp)}
                              >
                                🗑️
                              </button>
                            </div>
                          </div>
                          {resp.description && (
                            <p className="response-description">{resp.description}</p>
                          )}
                          <pre className="code-block-small">{resp.response_body}</pre>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="empty-text">No additional responses defined</p>
                  )}
                </>
              )}
            </div>
          </>
        )}

        {response && !isEditing && <ResponseViewer response={response} />}
      </div>

      <ResponseFormModal
        isOpen={showResponseForm}
        onClose={() => {
          setShowResponseForm(false);
          setEditingResponse(null);
        }}
        response={editingResponse}
        endpointId={endpoint.id}
        onSuccess={loadResponses}
      />

      <DeleteConfirmModal
        isOpen={!!deletingResponse}
        onClose={() => setDeletingResponse(null)}
        onConfirm={handleDeleteResponse}
        itemName={deletingResponse?.name}
        loading={deleteLoading}
      />
    </>
  );
}
