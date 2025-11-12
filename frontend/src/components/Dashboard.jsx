import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import EndpointList from './EndpointList';
import EndpointDetail from './EndpointDetail';
import { api } from '../api';

export default function Dashboard({ user, onLogout }) {
  const [collections, setCollections] = useState([]);
  const [selectedCollection, setSelectedCollection] = useState(null);
  const [endpoints, setEndpoints] = useState([]);
  const [selectedEndpoint, setSelectedEndpoint] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    loadCollections();
  }, []);

  const loadCollections = async () => {
    try {
      const data = await api.getCollections();
      setCollections(data);
      if (data.length > 0 && !selectedCollection) {
        handleSelectCollection(data[0]);
      } else if (selectedCollection) {
        const updated = data.find(c => c.id === selectedCollection.id);
        if (updated) {
          setSelectedCollection(updated);
        }
      }
    } catch (error) {
      console.error('Failed to load collections:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCollection = async (collection) => {
    setSelectedCollection(collection);
    setSelectedEndpoint(null);
    await loadEndpoints(collection.slug);
  };

  const loadEndpoints = async (slug) => {
    try {
      const data = await api.getEndpoints(slug);
      setEndpoints(data);
    } catch (error) {
      console.error('Failed to load endpoints:', error);
      setEndpoints([]);
    }
  };

  const handleRefreshCollections = () => {
    loadCollections();
  };

  const handleRefreshEndpoints = () => {
    if (selectedCollection) {
      loadEndpoints(selectedCollection.slug);
    }
  };

  if (loading) {
    return <div className="loading">Loading collections...</div>;
  }

  return (
    <div className="app">
      <Sidebar
        collections={collections}
        selectedCollection={selectedCollection}
        onSelectCollection={handleSelectCollection}
        user={user}
        onLogout={onLogout}
        onRefresh={handleRefreshCollections}
        collapsed={sidebarCollapsed}
        onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <div className="main-content">
        <EndpointList
          collection={selectedCollection}
          endpoints={endpoints}
          selectedEndpoint={selectedEndpoint}
          onSelectEndpoint={setSelectedEndpoint}
          onRefresh={handleRefreshEndpoints}
        />
        {selectedEndpoint && (
          <EndpointDetail
            endpoint={selectedEndpoint}
            collectionSlug={selectedCollection?.slug || ''}
            onRefresh={handleRefreshEndpoints}
          />
        )}
      </div>
    </div>
  );
}
