import React from 'react';
import { NavLink } from 'react-router-dom';
import { useAuth } from '../features/auth/AuthContext';

export const Sidebar: React.FC = () => {
  const { logout, user } = useAuth();

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: '📊' },
    { label: 'Songs & Transcoding', path: '/songs', icon: '🎵' },
    { label: 'Artists', path: '/artists', icon: '🎙️' },
    { label: 'Albums', path: '/albums', icon: '💿' },
    { label: 'Genres', path: '/genres', icon: '🏷️' },
    { label: 'User Roles', path: '/users', icon: '👥' },
    { label: 'Audit Logs', path: '/audit', icon: '📜' },
  ];

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col justify-between p-4 min-h-screen">
      <div>
        <div className="flex items-center gap-3 px-3 py-4 mb-6 border-b border-slate-800/80">
          <div className="w-10 h-10 bg-gradient-to-tr from-purple-600 to-indigo-500 rounded-xl flex items-center justify-center font-black text-white text-xl shadow-md">
            E
          </div>
          <div>
            <h2 className="font-bold text-white tracking-tight">Edify Admin</h2>
            <span className="text-xs text-purple-400 font-medium">Control Center</span>
          </div>
        </div>

        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition ${
                  isActive
                    ? 'bg-purple-600/20 text-purple-300 border border-purple-500/30'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="pt-4 border-t border-slate-800">
        <div className="flex items-center gap-3 px-3 mb-4">
          <div className="w-9 h-9 rounded-full bg-indigo-600/30 border border-indigo-500/40 flex items-center justify-center text-indigo-300 font-bold">
            {user?.email?.[0].toUpperCase() || 'A'}
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-semibold text-white truncate">{user?.first_name || 'Admin User'}</p>
            <p className="text-xs text-slate-400 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 hover:bg-red-500/20 text-slate-300 hover:text-red-300 rounded-xl text-sm font-medium transition border border-slate-700 hover:border-red-500/30"
        >
          <span>🚪</span> Sign Out
        </button>
      </div>
    </aside>
  );
};
