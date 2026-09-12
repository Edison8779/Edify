import React, { useEffect, useState } from 'react';
import { api, API_BASE_URL } from '../../api/client';
import { useToast } from '../../components/ui/Toast';
import type { Album, Artist } from '../../types';

export const AlbumsPage: React.FC = () => {
  const { showToast } = useToast();
  const [albums, setAlbums] = useState<Album[]>([]);
  const [artists, setArtists] = useState<Artist[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [artistId, setArtistId] = useState('');
  const [releaseYear, setReleaseYear] = useState('2026');
  const [coverFile, setCoverFile] = useState<File | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [albumRes, artistRes] = await Promise.all([api.get('/albums'), api.get('/artists')]);
      setAlbums(albumRes.data.data);
      setArtists(artistRes.data.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('title', title);
    formData.append('artist_id', artistId);
    if (releaseYear) formData.append('release_year', releaseYear);
    if (coverFile) formData.append('cover_file', coverFile);

    try {
      await api.post('/albums', formData);
      showToast(`Album "${title}" created successfully!`, 'success');
      setShowModal(false);
      setTitle('');
      setArtistId('');
      setCoverFile(null);
      fetchData();
    } catch (err: any) {
      showToast(err.response?.data?.error?.message || 'Failed to create album.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Albums Catalog</h1>
          <p className="text-slate-400 mt-1">Manage album collections and cover artwork.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold rounded-xl shadow-lg transition flex items-center gap-2"
        >
          <span>💿</span> Create Album
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
        {loading ? (
          <div className="col-span-4 text-slate-400 p-8 text-center">Loading albums...</div>
        ) : albums.length === 0 ? (
          <div className="col-span-4 text-slate-400 p-12 text-center glass-panel rounded-2xl">
            No albums found. Click <strong>Create Album</strong> to add one.
          </div>
        ) : (
          albums.map((album) => (
            <div key={album.id} className="glass-card p-4 rounded-2xl border border-slate-800 space-y-3">
              <div className="aspect-square rounded-xl bg-slate-900 overflow-hidden border border-slate-800 flex items-center justify-center text-4xl">
                {album.cover_url ? (
                  <img src={`${API_BASE_URL}/media/${album.cover_url}`} className="w-full h-full object-cover" />
                ) : (
                  '💿'
                )}
              </div>
              <div>
                <h3 className="font-bold text-white text-base truncate">{album.title}</h3>
                <p className="text-xs text-slate-400 truncate">{album.artist?.name || 'Unknown Artist'}</p>
                <p className="text-[10px] text-purple-400 mt-1 font-semibold">{album.release_year || '2026'}</p>
              </div>
            </div>
          ))
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-md p-6 rounded-2xl border border-slate-800 shadow-2xl">
            <h2 className="text-xl font-bold text-white mb-4">Create New Album</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Album Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  placeholder="Discovery"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Artist *</label>
                <select
                  required
                  value={artistId}
                  onChange={(e) => setArtistId(e.target.value)}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                >
                  <option value="">Select Artist</option>
                  {artists.map((a) => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Release Year</label>
                <input
                  type="number"
                  value={releaseYear}
                  onChange={(e) => setReleaseYear(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Cover Artwork Image</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setCoverFile(e.target.files?.[0] || null)}
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
                  Save Album
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
