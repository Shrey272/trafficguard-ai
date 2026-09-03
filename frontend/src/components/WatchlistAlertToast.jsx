import React, { useEffect, useState } from 'react';
import { useRealtime } from '../context/RealtimeContext';
import { AlertCircle, X } from 'lucide-react';

const WatchlistAlertToast = () => {
  const { lastWatchlistAlert } = useRealtime();
  const [show, setShow] = useState(false);
  const [alertData, setAlertData] = useState(null);

  useEffect(() => {
    if (lastWatchlistAlert) {
      setAlertData(lastWatchlistAlert);
      setShow(true);
      const timer = setTimeout(() => {
        setShow(false);
      }, 8000); // 8 seconds visible
      return () => clearTimeout(timer);
    }
  }, [lastWatchlistAlert]);

  if (!show || !alertData) return null;

  return (
    <div className="fixed bottom-6 right-6 z-[100] animate-in slide-in-from-bottom-5 fade-in duration-300">
      <div className="bg-rose-900 border-2 border-rose-500 rounded-lg shadow-2xl p-4 max-w-sm flex gap-4">
        <div className="text-rose-400 mt-1">
          <AlertCircle size={24} className="animate-pulse" />
        </div>
        <div className="flex-1">
          <h3 className="text-rose-100 font-bold text-lg">Watchlist Match Alert!</h3>
          <p className="text-rose-200 text-sm mt-1">
            <span className="font-mono bg-rose-950 px-1 py-0.5 rounded">{alertData.plate_text}</span> detected at <strong>{alertData.camera_id}</strong>
          </p>
          <div className="mt-2 text-xs text-rose-300">
            <strong>Category:</strong> {alertData.category}<br />
            <strong>Confidence:</strong> {(alertData.confidence * 100).toFixed(1)}%<br />
            <strong>Time:</strong> {new Date(alertData.timestamp).toLocaleTimeString()}
          </div>
        </div>
        <button onClick={() => setShow(false)} className="text-rose-400 hover:text-white items-start">
          <X size={20} />
        </button>
      </div>
    </div>
  );
};

export default WatchlistAlertToast;
