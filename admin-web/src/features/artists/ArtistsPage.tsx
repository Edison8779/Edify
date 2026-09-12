import React, { useEffect, useState } from 'react';
import { api, API_BASE_URL } from '../../api/client';
import { useToast } from '../../components/ui/Toast';
import type { Artist } from '../../types';

export const ArtistsPage: React.FC = () => {
  const { showToast } = useToast();
  const [artists, setArtists] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [name, setName] = useState('');
  const [bio, setBio] = useState('');
  const [avatarFile, setAvatarFile] = useState<File | null>(null);

  const fetchArtists = async () => {
    setLoading(true);
    try {
      const res = await api.get('/artists');
      setArtists(res.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArtists();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', name);
    if (bio) formData.append('bio', bio);
    if (avatarFile) formData.append('avatar_file', avatarFile);

    try {
      await api.post('/artists', formData);
      showToast(`Artist "${name}" created successfully!`, 'success');
      setShowModal(false);
      setName('');
      setBio('');
      setAvatarFile(null);
      fetchArtists();
    } catch (err: any) {
      showToast(err.response?.data?.error?.message || 'Failed to create artist.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Artists Management</h1>
          <p className="text-slate-400 mt-1">Add and manage music artists & creators.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold rounded-xl shadow-lg transition flex items-center gap-2"
        >
          <span>🎙️</span> Add Artist
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {loading ? (
          <div className="col-span-3 text-slate-400 p-8 text-center">Loading artists...</div>
        ) : artists.length === 0 ? (
          <div className="col-span-3 text-slate-400 p-12 text-center glass-panel rounded-2xl">
            No artists found. Click <strong>Add Artist</strong> to create one.
          </div>
        ) : (
          artists.map((artist) => (
            <div key={artist.id} className="glass-card p-6 rounded-2xl border border-slate-800 flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center text-2xl font-bold text-purple-400 overflow-hidden border border-slate-700 shrink-0">
                {artist.avatar_url ? (
                  <img src={`${API_BASE_URL}/media/${artist.avatar_url}`} className="w-full h-full object-cover" />
                ) : (
                  artist.name[0].toUpperCase()
                )}
              </div>
              <div>
                <h3 className="font-bold text-white text-lg">{artist.name}</h3>
                <p className="text-xs text-slate-400 line-clamp-2 mt-1">{artist.bio || 'No biography provided.'}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-800 shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-4">Add Artist Profile</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Artist Name *</label>
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  placeholder="Daft Punk"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Biography</label>
                <textarea
                  value={bio}
                  onChange={(e) => setBio(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500 h-24"
                  placeholder="Electronic music pioneer duo..."
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Avatar Image</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setAvatarFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-purple-600/20 file:text-purple-300 hover:file:bg-purple-600/30"
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
                  Save Artist
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
