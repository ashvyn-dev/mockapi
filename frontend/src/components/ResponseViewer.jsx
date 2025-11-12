export default function ResponseViewer({ response }) {
  const getStatusColor = (status) => {
    if (status >= 200 && status < 300) return '#10b981';
    if (status >= 300 && status < 400) return '#3b82f6';
    if (status >= 400 && status < 500) return '#f59e0b';
    if (status >= 500) return '#ef4444';
    return '#6b7280';
  };

  return (
    <div className="response-viewer">
      <div className="response-header">
        <h4>Response</h4>
        <div className="response-meta">
          <span
            className="status-badge"
            style={{ backgroundColor: getStatusColor(response.status) }}
          >
            {response.status} {response.statusText}
          </span>
          <span className="time-badge">{response.time}ms</span>
        </div>
      </div>

      <div className="response-body">
        <div className="section-label">Body</div>
        <pre className="code-block">
          {JSON.stringify(response.data, null, 2)}
        </pre>
      </div>

      <div className="response-headers">
        <div className="section-label">Headers</div>
        <div className="headers-list">
          {Object.entries(response.headers).map(([key, value]) => (
            <div key={key} className="header-item">
              <span className="header-key">{key}:</span>
              <span className="header-value">{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
