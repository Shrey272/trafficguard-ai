import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Plus, Trash2 } from 'lucide-react';

const WatchlistManagement = () => {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newPlate, setNewPlate] = useState('');
  const [newCategory, setNewCategory] = useState('SUSPECT');
  const [newNotes, setNewNotes] = useState('');
  const [error, setError] = useState(null);
  const { authFetch } = useAuth();

  const fetchRecords = async () => {
    try {
      const res = await authFetch('/api/watchlist');
      if (res.ok) {
        const data = await res.json();
        setRecords(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newPlate.trim()) return;
    try {
      setError(null);
      const res = await authFetch('/api/watchlist', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plate_text: newPlate, category: newCategory, notes: newNotes })
      });
      if (res.ok) {
        setNewPlate('');
        setNewNotes('');
        fetchRecords();
      } else {
        const d = await res.json();
        setError(d.detail || 'Failed to add plate');
      }
    } catch (err) {
      setError('Network error');
    }
  };

  const handleDelete = async (id) => {
    try {
      const res = await authFetch(`/api/watchlist/${id}`, { method: 'DELETE' });
      if (res.ok) {
        fetchRecords();
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Demo Watchlist Management</h1>
      
      <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
        <h2 className="text-lg font-semibold text-gray-200 mb-4">Add Plate to Watchlist</h2>
        <form onSubmit={handleAdd} className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-400 mb-1">Plate Number</label>
            <input type="text" value={newPlate} onChange={e => setNewPlate(e.target.value)}
                   className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white focus:ring-blue-500 focus:border-blue-500" 
                   placeholder="e.g. GJ05AB1234" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">Category</label>
            <select value={newCategory} onChange={e => setNewCategory(e.target.value)}
                    className="bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white">
              <option value="SUSPECT">Suspect</option>
              <option value="STOLEN">Stolen</option>
              <option value="WANTED">Wanted</option>
            </select>
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-400 mb-1">Notes</label>
            <input type="text" value={newNotes} onChange={e => setNewNotes(e.target.value)}
                   className="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-2 text-white" 
                   placeholder="Optional details" />
          </div>
          <button type="submit" className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg flex items-center h-[42px]">
            <Plus className="w-5 h-5 mr-2" /> Add
          </button>
        </form>
        {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
      </div>

      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <table className="min-w-full divide-y divide-gray-700">
          <thead className="bg-gray-900/50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Plate Text</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Category</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Notes</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Added At</th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {records.map(record => (
              <tr key={record.id} className="hover:bg-gray-750">
                <td className="px-6 py-4 whitespace-nowrap font-mono text-gray-200">{record.plate_text}</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    record.category === 'STOLEN' ? 'bg-red-900/50 text-red-400' :
                    record.category === 'WANTED' ? 'bg-purple-900/50 text-purple-400' :
                    'bg-yellow-900/50 text-yellow-400'
                  }`}>
                    {record.category}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-400">{record.notes}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">{new Date(record.created_at).toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button onClick={() => handleDelete(record.id)} className="text-red-400 hover:text-red-300">
                    <Trash2 className="w-5 h-5 inline" />
                  </button>
                </td>
              </tr>
            ))}
            {records.length === 0 && !loading && (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">No records found</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default WatchlistManagement;
