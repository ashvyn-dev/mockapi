import Modal from './Modal';

export default function DeleteConfirmModal({ isOpen, onClose, onConfirm, itemName, loading }) {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Confirm Delete">
      <div className="delete-confirm">
        <p>Are you sure you want to delete <strong>{itemName}</strong>?</p>
        <p className="warning-text">This action cannot be undone.</p>

        <div className="form-actions">
          <button onClick={onClose} className="btn-secondary" disabled={loading}>
            Cancel
          </button>
          <button onClick={onConfirm} className="btn-danger" disabled={loading}>
            {loading ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>
    </Modal>
  );
}
