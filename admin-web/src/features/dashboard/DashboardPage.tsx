import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';
import type { AdminStats } from '../../types';
import { Link } from 'react-router-dom';

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/admin/stats')
      .then((res) => setStats(res.data.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const formatBytes = (bytes: number) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const statCards = [
    { label: 'Total Songs', value: stats?.total_songs ?? 0, icon: '🎵', color: 'from-purple-500 to-indigo-600', link: '/songs' },
    { label: 'Total Artists', value: stats?.total_artists ?? 0, icon: '🎙️', color: 'from-indigo-500 to-blue-600', link: '/artists' },
    { label: 'Total Albums', value: stats?.total_albums ?? 0, icon: '💿', color: 'from-blue-500 to-cyan-600', link: '/albums' },
    { label: 'Registered Users', value: stats?.total_users ?? 0, icon: '👥', color: 'from-emerald-500 to-teal-600', link: '/users' },
    { label: 'Music Storage', value: formatBytes(stats?.total_storage_bytes ?? 0), icon: '💾', color: 'from-pink-500 to-rose-600', link: '/songs' },
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">System Overview</h1>
        <p className="text-slate-400 mt-1">Real-time statistics & quick operations across the Edify ecosystem.</p>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-36 glass-card rounded-2xl animate-pulse"></div>
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {statCards.map((card, idx) => (
            <Link
              key={idx}
              to={card.link}
              className="glass-card p-6 rounded-2xl border border-slate-800 hover:border-purple-500/40 transition group relative overflow-hidden"
            >
              <div className="flex items-center justify-between mb-4">
                <span className="text-3xl">{card.icon}</span>
                <span className="text-xs font-semibold px-2.5 py-1 bg-slate-800 text-slate-300 rounded-full group-hover:bg-purple-500/20 group-hover:text-purple-300 transition">
                  Manage &rarr;
                </span>
              </div>
              <h3 className="text-sm font-medium text-slate-400 mb-1">{card.label}</h3>
              <p className="text-3xl font-extrabold text-white">{card.value}</p>
            </Link>
          ))}
        </div>
      )}

      <div className="glass-panel p-6 rounded-2xl border border-slate-800">
        <h2 className="text-lg font-bold text-white mb-4">Quick Admin Actions</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/songs"
            className="p-4 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-xl flex items-center gap-3 transition"
          >
            <span className="text-2xl">📤</span>
            <div>
              <p className="font-semibold text-white text-sm">Upload Song</p>
              <p className="text-xs text-slate-400">Add track & audio variants</p>
            </div>
          </Link>

          <Link
            to="/artists"
            className="p-4 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-xl flex items-center gap-3 transition"
          >
            <span className="text-2xl">🎙️</span>
            <div>
              <p className="font-semibold text-white text-sm">New Artist</p>
              <p className="text-xs text-slate-400">Add artist profile</p>
            </div>
          </Link>

          <Link
            to="/albums"
            className="p-4 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-xl flex items-center gap-3 transition"
          >
            <span className="text-2xl">💿</span>
            <div>
              <p className="font-semibold text-white text-sm">Create Album</p>
              <p className="text-xs text-slate-400">Add album & artwork</p>
            </div>
          </Link>

          <Link
            to="/audit"
            className="p-4 bg-slate-900/80 hover:bg-slate-800 border border-slate-800 rounded-xl flex items-center gap-3 transition"
          >
            <span className="text-2xl">📜</span>
            <div>
              <p className="font-semibold text-white text-sm">View Audit Logs</p>
              <p className="text-xs text-slate-400">Security & action audit</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};
