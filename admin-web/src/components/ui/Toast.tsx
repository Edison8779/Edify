import React, { createContext, useCallback, useContext, useState, useRef, useEffect } from 'react';

// ── Types ──────────────────────────────────────────────────────
type ToastType = 'success' | 'error' | 'warning' | 'info';

interface Toast {
  id: string;
  message: string;
  type: ToastType;
  duration: number;
  exiting?: boolean;
}

interface ToastContextValue {
  showToast: (message: string, type?: ToastType, duration?: number) => void;
}

// ── Context ────────────────────────────────────────────────────
const ToastContext = createContext<ToastContextValue | null>(null);

export const useToast = (): ToastContextValue => {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within <ToastProvider>');
  return ctx;
};

// ── Icon per type ──────────────────────────────────────────────
const icons: Record<ToastType, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
};

// ── Style tokens ───────────────────────────────────────────────
const typeStyles: Record<ToastType, string> = {
  success:
    'border-emerald-500/40 bg-emerald-500/10 text-emerald-300 shadow-emerald-500/20',
  error:
    'border-red-500/40 bg-red-500/10 text-red-300 shadow-red-500/20',
  warning:
    'border-amber-500/40 bg-amber-500/10 text-amber-300 shadow-amber-500/20',
  info:
    'border-blue-500/40 bg-blue-500/10 text-blue-300 shadow-blue-500/20',
};

const iconContainerStyles: Record<ToastType, string> = {
  success: 'bg-emerald-500/20 text-emerald-400',
  error: 'bg-red-500/20 text-red-400',
  warning: 'bg-amber-500/20 text-amber-400',
  info: 'bg-blue-500/20 text-blue-400',
};

const progressBarStyles: Record<ToastType, string> = {
  success: 'bg-emerald-400',
  error: 'bg-red-400',
  warning: 'bg-amber-400',
  info: 'bg-blue-400',
};

// ── Single Toast Item ──────────────────────────────────────────
const ToastItem: React.FC<{
  toast: Toast;
  onRemove: (id: string) => void;
}> = ({ toast, onRemove }) => {
  const [progress, setProgress] = useState(100);
  const startTime = useRef(Date.now());

  useEffect(() => {
    const frame = () => {
      const elapsed = Date.now() - startTime.current;
      const remaining = Math.max(0, 100 - (elapsed / toast.duration) * 100);
      setProgress(remaining);
      if (remaining > 0) requestAnimationFrame(frame);
    };
    const raf = requestAnimationFrame(frame);

    const timeout = setTimeout(() => onRemove(toast.id), toast.duration);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(timeout);
    };
  }, [toast.id, toast.duration, onRemove]);

  return (
    <div
      className={`
        relative overflow-hidden rounded-xl border backdrop-blur-md
        shadow-lg px-4 py-3 flex items-start gap-3 min-w-[320px] max-w-[440px]
        transition-all duration-300 ease-out
        ${toast.exiting ? 'animate-toast-exit' : 'animate-toast-enter'}
        ${typeStyles[toast.type]}
      `}
      role="alert"
    >
      {/* Icon */}
      <div
        className={`w-7 h-7 rounded-lg flex items-center justify-center text-sm font-bold shrink-0 mt-0.5 ${iconContainerStyles[toast.type]}`}
      >
        {icons[toast.type]}
      </div>

      {/* Message */}
      <p className="text-sm font-medium leading-snug flex-1 pt-0.5">{toast.message}</p>

      {/* Close button */}
      <button
        onClick={() => onRemove(toast.id)}
        className="text-white/40 hover:text-white/80 text-lg leading-none transition shrink-0 mt-0.5"
        aria-label="Dismiss"
      >
        ×
      </button>

      {/* Progress bar */}
      <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-white/5">
        <div
          className={`h-full transition-none ${progressBarStyles[toast.type]}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
};

// ── Provider ───────────────────────────────────────────────────
let toastCounter = 0;

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const showToast = useCallback(
    (message: string, type: ToastType = 'success', duration = 4000) => {
      const id = `toast-${++toastCounter}-${Date.now()}`;
      setToasts((prev) => [...prev, { id, message, type, duration }]);
    },
    [],
  );

  const removeToast = useCallback((id: string) => {
    // Mark as exiting for slide-out animation
    setToasts((prev) => prev.map((t) => (t.id === id ? { ...t, exiting: true } : t)));
    // Remove after animation completes
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 280);
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}

      {/* Toast container — fixed top-right */}
      <div
        className="fixed top-6 right-6 z-[9999] flex flex-col gap-3 pointer-events-none"
        aria-live="polite"
      >
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} onRemove={removeToast} />
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
