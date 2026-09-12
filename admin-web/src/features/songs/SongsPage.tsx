import React, { useEffect, useState } from 'react';
import { api, API_BASE_URL } from '../../api/client';
import { useToast } from '../../components/ui/Toast';
import type { Song, Artist, Album, Genre } from '../../types';

export const SongsPage: React.FC = () => {
  const { showToast } = useToast();
  const [songs, setSongs] = useState<Song[]>([]);
  const [artists, setArtists] = useState<Artist[]>([]);
  const [albums, setAlbums] = useState<Album[]>([]);
  const [genres, setGenres] = useState<Genre[]>([]);
  const [loading, setLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  // Upload Form State
  const [showModal, setShowModal] = useState(false);
  const [title, setTitle] = useState('');
  const [artistId, setArtistId] = useState('');
  const [albumId, setAlbumId] = useState('');
  const [genreId, setGenreId] = useState('');
  const [duration, setDuration] = useState('180');
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [coverFile, setCoverFile] = useState<File | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [songsRes, artistsRes, albumsRes, genresRes] = await Promise.all([
        api.get('/songs'),
        api.get('/artists'),
        api.get('/albums'),
        api.get('/genres'),
      ]);
      setSongs(songsRes.data.data);
      const fetchedArtists = artistsRes.data.data || [];
      setArtists(fetchedArtists);
      setAlbums(albumsRes.data.data || []);
      setGenres(genresRes.data.data || []);
      if (fetchedArtists.length > 0 && !artistId) {
        setArtistId(fetchedArtists[0].id);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) {
      showToast('Please enter a song title.', 'warning');
      return;
    }
    if (!artistId) {
      showToast('Please select an artist.', 'warning');
      return;
    }
    if (!audioFile) {
      showToast('Please select an audio file.', 'warning');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('title', title.trim());
    formData.append('artist_id', artistId);
    formData.append('audio_file', audioFile);
    if (albumId) formData.append('album_id', albumId);
    if (genreId) formData.append('genre_id', genreId);
    if (duration) formData.append('duration_seconds', duration);
    if (coverFile) formData.append('cover_file', coverFile);

    try {
      await api.post('/songs/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      showToast(`Song "${title.trim()}" uploaded successfully! Transcoding started.`, 'success');
      setShowModal(false);
      setTitle('');
      setAudioFile(null);
      setCoverFile(null);
      setDuration('180');
      fetchData();
    } catch (err: any) {
      console.error('Upload error:', err);
      showToast(
        err.response?.data?.error?.message || err.message || 'Upload failed. Please try again.',
        'error',
      );
    } finally {
      setIsUploading(false);
    }
  };


  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this song?')) return;
    try {
      await api.delete(`/songs/${id}`);
      showToast('Song deleted successfully.', 'success');
      fetchData();
    } catch (err: any) {
      showToast(err.response?.data?.error?.message || 'Failed to delete song.', 'error');
    }
  };

  const toggleActive = async (song: Song) => {
    try {
      await api.put(`/songs/${song.id}`, { is_active: !song.is_active });
      showToast(
        `Song "${song.title}" ${song.is_active ? 'disabled' : 'activated'} successfully.`,
        'success',
      );
      fetchData();
    } catch (err: any) {
      showToast('Failed to update song status.', 'error');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Music Catalog & Transcoding</h1>
          <p className="text-slate-400 mt-1">Upload tracks, monitor FFmpeg bitrate variants (64k/128k/256k), and manage songs.</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-5 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold rounded-xl shadow-lg shadow-purple-600/30 transition flex items-center gap-2"
        >
          <span>📤</span> Upload Track
        </button>
      </div>

      {/* Songs Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-400">Loading catalog...</div>
        ) : songs.length === 0 ? (
          <div className="p-12 text-center text-slate-400">
            <span className="text-4xl block mb-2">🎵</span>
            No songs uploaded yet. Click <strong>Upload Track</strong> to add music.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs font-semibold text-slate-400 uppercase border-b border-slate-800">
                <tr>
                  <th className="px-6 py-4">Title & Artist</th>
                  <th className="px-6 py-4">Album</th>
                  <th className="px-6 py-4">Genre</th>
                  <th className="px-6 py-4">Quality Variants</th>
                  <th className="px-6 py-4">Preview</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {songs.map((song) => (
                  <tr key={song.id} className="hover:bg-slate-900/40 transition">
                    <td className="px-6 py-4 font-medium text-white flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center font-bold text-purple-400 overflow-hidden border border-slate-700">
                        {song.album?.cover_url ? (
                          <img src={`${API_BASE_URL}/media/${song.album.cover_url}`} className="w-full h-full object-cover" />
                        ) : (
                          '🎵'
                        )}
                      </div>
                      <div>
                        <p className="text-white font-semibold">{song.title}</p>
                        <p className="text-xs text-slate-400">{song.artist?.name || 'Unknown Artist'}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-400">{song.album?.title || 'Single'}</td>
                    <td className="px-6 py-4 text-slate-400">{song.genre?.name || '—'}</td>
                    <td className="px-6 py-4">
                      <div className="flex gap-1.5 flex-wrap">
                        {['64k', '128k', '256k'].map((q) => {
                          const v = song.variants.find((varItem) => varItem.quality === q);
                          return (
                            <span
                              key={q}
                              className={`text-[10px] font-bold px-2 py-0.5 rounded-md ${
                                v?.status === 'ready'
                                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                                  : v?.status === 'processing'
                                  ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30 animate-pulse'
                                  : 'bg-slate-800 text-slate-500'
                              }`}
                            >
                              {q}
                            </span>
                          );
                        })}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <audio
                        controls
                        src={`${API_BASE_URL}/songs/${song.id}/stream`}
                        className="h-8 w-44 rounded-lg"
                      />
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => toggleActive(song)}
                        className={`text-xs font-semibold px-3 py-1 rounded-full transition ${
                          song.is_active
                            ? 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30'
                            : 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                        }`}
                      >
                        {song.is_active ? 'Active' : 'Disabled'}
                      </button>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button
                        onClick={() => handleDelete(song.id)}
                        className="text-red-400 hover:text-red-300 font-semibold text-xs px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 rounded-lg border border-red-500/20 transition"
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Upload Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
          <div className="glass-panel w-full max-w-lg p-6 rounded-2xl border border-slate-800 shadow-2xl relative">
            <h2 className="text-xl font-bold text-white mb-4">Upload New Song</h2>
            <form onSubmit={handleUpload} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Song Title *</label>
                <input
                  type="text"
                  required
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  placeholder="Midnight Resonance"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
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
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Album</label>
                  <select
                    value={albumId}
                    onChange={(e) => setAlbumId(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  >
                    <option value="">Single / No Album</option>
                    {albums.map((al) => (
                      <option key={al.id} value={al.id}>{al.title}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Genre</label>
                  <select
                    value={genreId}
                    onChange={(e) => setGenreId(e.target.value)}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  >
                    <option value="">Select Genre</option>
                    {genres.map((g) => (
                      <option key={g.id} value={g.id}>{g.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Duration (Sec)</label>
                  <input
                    type="number"
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Audio File (MP3/WAV/FLAC) *</label>
                <input
                  type="file"
                  accept="audio/*"
                  required
                  onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-purple-600/20 file:text-purple-300 hover:file:bg-purple-600/30"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-300 uppercase mb-1">Cover Artwork (Optional)</label>
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setCoverFile(e.target.files?.[0] || null)}
                  className="w-full text-xs text-slate-400 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-600/20 file:text-indigo-300 hover:file:bg-indigo-600/30"
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
                  disabled={isUploading}
                  className="px-5 py-2 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl text-sm font-semibold transition disabled:opacity-50"
                >
                  {isUploading ? 'Uploading & Transcoding...' : 'Upload & Transcode'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
