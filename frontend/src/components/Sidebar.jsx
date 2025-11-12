import { useState } from 'react';
import CollectionFormModal from './CollectionFormModal';
import DeleteConfirmModal from './DeleteConfirmModal';
import { api } from '../api';

export default function Sidebar({
  collections,
  selectedCollection,
  onSelectCollection,
  user,
  onLogout,
  onRefresh,
  collapsed,
  onToggleCollapse
}) {
  const [showCollectionForm, setShowCollectionForm] = useState(false);
  const [editingCollection, setEditingCollection] = useState(null);
  const [deletingCollection, setDeletingCollection] = useState(null);
  const [deleteLoading, setDeleteLoading] = useState(false);
  const [collectionsExpanded, setCollectionsExpanded] = useState(true);

  const handleEdit = (e, collection) => {
    e.stopPropagation();
    setEditingCollection(collection);
    setShowCollectionForm(true);
  };

  const handleDelete = (e, collection) => {
    e.stopPropagation();
    setDeletingCollection(collection);
  };

  const confirmDelete = async () => {
    setDeleteLoading(true);
    try {
      await api.deleteCollection(deletingCollection.slug);
      setDeletingCollection(null);
      onRefresh();
    } catch (error) {
      console.error('Failed to delete collection:', error);
      alert('Failed to delete collection');
    } finally {
      setDeleteLoading(false);
    }
  };

  return (
    <>
      <div className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
        <button
          className="sidebar-toggle"
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand' : 'Collapse'}
        >
          {collapsed ? '»' : '«'}
        </button>

        {!collapsed && (
          <>
            <div className="sidebar-header">
              <h1>HF Mock API</h1>
              <p className="subtitle">API Testing Dashboard</p>
            </div>

            <div className="user-info">
              <div className="user-avatar">{user.username[0].toUpperCase()}</div>
              <div className="user-details">
                <div className="user-name">{user.username}</div>
                <button onClick={onLogout} className="logout-button">
                  Logout
                </button>
              </div>
            </div>

            <div className="collections">
              <div className="section-header">
                <div
                  className="section-title-clickable"
                  onClick={() => setCollectionsExpanded(!collectionsExpanded)}
                >
                  <span className="collapse-icon">{collectionsExpanded ? '▼' : '▶'}</span>
                  <span className="section-title">Collections ({collections.length})</span>
                </div>
                <button
                  className="btn-icon"
                  onClick={() => {
                    setEditingCollection(null);
                    setShowCollectionForm(true);
                  }}
                  title="New Collection"
                >
                  +
                </button>
              </div>

              {collectionsExpanded && (
                <div className="collections-list">
                  {collections.map((collection) => (
                    <div
                      key={collection.id}
                      className={`collection-item ${
                        selectedCollection?.id === collection.id ? 'active' : ''
                      }`}
                      onClick={() => onSelectCollection(collection)}
                    >
                      <div className="collection-icon">📁</div>
                      <div className="collection-info">
                        <div className="collection-name">{collection.slug}</div>
                        <div className="collection-desc">{collection.name}</div>
                      </div>
                      <div className="collection-actions">
                        <button
                          className="action-btn"
                          onClick={(e) => handleEdit(e, collection)}
                          title="Edit"
                        >
                          ✏️
                        </button>
                        <button
                          className="action-btn"
                          onClick={(e) => handleDelete(e, collection)}
                          title="Delete"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </>
        )}
      </div>

      <CollectionFormModal
        isOpen={showCollectionForm}
        onClose={() => {
          setShowCollectionForm(false);
          setEditingCollection(null);
        }}
        collection={editingCollection}
        onSuccess={onRefresh}
      />

      <DeleteConfirmModal
        isOpen={!!deletingCollection}
        onClose={() => setDeletingCollection(null)}
        onConfirm={confirmDelete}
        itemName={deletingCollection?.name}
        loading={deleteLoading}
      />
    </>
  );
}
