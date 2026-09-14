import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { useToast } from '../../components/ui/Toast';
import type { Genre } from '../../types';

export const GenresPage: React.FC = () => {
  const { showToast } = useToast();
  const [genres, setGenres] = useState<Genre[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const fetchGenres = async () => {
    setLoading(true);
    try {
      const res = await api.get('/genres');
      setGenres(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGenres();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post('/genres', { name, description });
      showToast(`Genre "${name}" created successfully!`, 'success');
      setShowModal(false);
      setName('');
      setDescription('');
      fetchGenres();
    } catch (err: any) {
      showToast(err.response?.data?.error?.message || 'Failed to create genre.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Music Genres</h1>
          <p className="text-slate-400 mt-1">Configure categories & style taxonomies.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold rounded-xl shadow-lg transition flex items-center gap-2"
        >
          <span>🏷️</span> Add Genre
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-3 text-slate-400 p-8 text-center">Loading genres...</div>
        ) : (
          genres.map((genre) => (
            <div key={genre.id} className="glass-card p-6 rounded-2xl border border-slate-800 space-y-2">
              <div className="flex justify-between items-center">
                <h3 className="font-bold text-white text-lg">{genre.name}</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {genre.slug}
                </span>
              </div>
              <p className="text-xs text-slate-400">{genre.description || 'No description provided.'}</p>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-800 shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-4">Add Music Genre</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Genre Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  placeholder="Lo-Fi Beats"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Description</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500 h-24"
                  placeholder="Chill, relaxing instrumental hip hop beats..."
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl text-sm font-semibold transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-sm font-semibold transition"
                >
                  Save Genre
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
