import React, { useState, useEffect } from 'react';
import { Search, ShieldAlert, Car, Camera, MapPin, Clock, ArrowRight, CheckCircle, AlertTriangle, RefreshCw, FileText } from 'lucide-react';

const ANPR = () => {
  const [plates, setPlates] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch recent plate recognitions from backend
  const fetchPlates = async () => {
    try {
      const response = await fetch('/api/plates/');
      if (response.ok) {
        const data = await response.json();
        setPlates(data);
      }
    } catch (err) {
      console.error("Error fetching plate records:", err);
    }
  };

  useEffect(() => {
    fetchPlates();
    const interval = setInterval(fetchPlates, 10000);
    return () => clearInterval(interval);
  }, []);

  // Search vehicle movement history
  const handleSearch = async (e, plateNum) => {
    if (e) e.preventDefault();
    const targetPlate = plateNum || searchQuery;
    if (!targetPlate.trim()) return;

    setLoading(true);
    setError('');
    setSearchResults(null);

    try {
      const response = await fetch(`/api/plates/search?plate_number=${encodeURIComponent(targetPlate.trim())}`);
      if (!response.ok) {
        throw new Error(`No sightings found for '${targetPlate}'`);
      }
      const data = await response.json();
      setSearchResults(data);
    } catch (err) {
      setError(err.message || 'Error searching vehicle plate');
    } finally {
      setLoading(false);
    }
  };

  const sampleSearch = (plate) => {
    setSearchQuery(plate);
    handleSearch(null, plate);
  };

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-dark-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs px-2.5 py-1 rounded-md font-semibold tracking-wider flex items-center gap-1.5">
              <span className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></span>
              ANPR LIVE ENGINE
            </span>
            <span className="text-xs text-slate-400">SURAT TRAFFIC COMMAND CENTER</span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Automatic Number Plate Recognition (ANPR)</h1>
          <p className="text-sm text-slate-400">Real-time vehicle registration detection and multi-camera movement tracing</p>
        </div>

        <button 
          onClick={fetchPlates}
          className="self-start md:self-auto bg-slate-800 hover:bg-slate-700 text-slate-300 border border-dark-border px-3 py-2 rounded-lg text-sm flex items-center gap-2 transition-colors"
        >
          <RefreshCw size={16} />
          Refresh Feed
        </button>
      </div>

      {/* Metric Stats Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-dark-panel border border-dark-border rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-lg">
            <Car size={24} />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Scanned Today</p>
            <h3 className="text-2xl font-bold text-white">1,482</h3>
            <p className="text-xs text-emerald-400 font-medium mt-0.5">↑ 12% vs yesterday</p>
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-rose-500/10 text-rose-400 border border-rose-500/20 rounded-lg">
            <ShieldAlert size={24} />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Flagged / Suspicious</p>
            <h3 className="text-2xl font-bold text-white">2</h3>
            <p className="text-xs text-rose-400 font-medium mt-0.5">Instant Alert Dispatched</p>
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 rounded-lg">
            <Camera size={24} />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">Active ANPR Cameras</p>
            <h3 className="text-2xl font-bold text-white">5 / 5</h3>
            <p className="text-xs text-indigo-400 font-medium mt-0.5">100% Coverage Active</p>
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-xl p-4 flex items-center gap-4">
          <div className="p-3 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-lg">
            <CheckCircle size={24} />
          </div>
          <div>
            <p className="text-xs text-slate-400 font-medium">AI Accuracy Rate</p>
            <h3 className="text-2xl font-bold text-white">97.8%</h3>
            <p className="text-xs text-slate-400 font-medium mt-0.5">YOLOv8 + ByteTrack OCR</p>
          </div>
        </div>
      </div>

      {/* Vehicle Tracing Search Section */}
      <div className="bg-dark-panel border border-dark-border rounded-xl p-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              <Search className="text-indigo-400" size={20} />
              Vehicle Movement Tracing
            </h2>
            <p className="text-sm text-slate-400">Search any vehicle registration number to trace its exact timeline across city cameras</p>
          </div>

          {/* Quick preset chips */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-slate-400">Try presets:</span>
            <button 
              onClick={() => sampleSearch('GJ-05-AB-1234')}
              className="bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs px-2.5 py-1 rounded-md font-mono transition-colors"
            >
              GJ-05-AB-1234 (3 Sightings)
            </button>
            <button 
              onClick={() => sampleSearch('GJ-05-XY-9876')}
              className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 text-xs px-2.5 py-1 rounded-md font-mono transition-colors"
            >
              GJ-05-XY-9876 (Flagged)
            </button>
          </div>
        </div>

        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3.5 top-3 text-slate-400" size={18} />
            <input 
              type="text"
              placeholder="Enter Registration Plate Number (e.g. GJ-05-AB-1234)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-900 border border-dark-border rounded-lg pl-10 pr-4 py-2.5 text-white font-mono text-sm placeholder:font-sans placeholder:text-slate-500 focus:outline-none focus:border-indigo-500 transition-colors"
            />
          </div>
          <button 
            type="submit"
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-6 py-2.5 rounded-lg text-sm flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            {loading ? <RefreshCw className="animate-spin" size={16} /> : <Search size={16} />}
            Trace Movement
          </button>
        </form>

        {error && (
          <div className="bg-rose-500/10 border border-rose-500/20 text-rose-400 p-3 rounded-lg text-sm flex items-center gap-2">
            <AlertTriangle size={16} />
            {error}
          </div>
        )}

        {/* Search Results / Vehicle Timeline Trace */}
        {searchResults && (
          <div className="mt-6 border border-slate-700/60 rounded-xl p-5 bg-slate-900/60 space-y-4 animate-in fade-in duration-300">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-700/60 pb-3 gap-2">
              <div className="flex items-center gap-3">
                <span className="bg-slate-800 text-white font-mono text-lg font-bold px-3 py-1 rounded-md border border-slate-700">
                  {searchResults.plate_number}
                </span>
                <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 text-xs px-2.5 py-1 rounded-md font-semibold">
                  {searchResults.total_sightings} Sightings Tracked
                </span>
              </div>
              <span className="text-xs text-slate-400">
                Last Spotted: {new Date(searchResults.last_seen).toLocaleTimeString()}
              </span>
            </div>

            {/* Camera Sequence Timeline */}
            <div className="space-y-3">
              <h4 className="text-xs font-semibold text-slate-400 tracking-wider uppercase">Multi-Camera Trajectory Route</h4>
              
              <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-indigo-500/40">
                {searchResults.sightings.map((sighting, idx) => (
                  <div key={sighting.id || idx} className="relative flex flex-col sm:flex-row sm:items-center justify-between bg-dark-panel border border-dark-border rounded-lg p-3 gap-2">
                    {/* Timeline Marker Dot */}
                    <div className="absolute -left-[23px] top-4 w-3.5 h-3.5 rounded-full bg-indigo-500 border-2 border-slate-900 ring-2 ring-indigo-500/30"></div>

                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-slate-800 text-slate-300 rounded">
                        <MapPin size={18} />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-white text-sm">{sighting.camera_name}</span>
                          <span className="text-xs font-mono text-slate-400">({sighting.camera_id})</span>
                        </div>
                        <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                          <Clock size={12} />
                          {new Date(sighting.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <span className="text-xs text-slate-400">Vehicle: <strong className="text-slate-200">{sighting.vehicle_type}</strong></span>
                      <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2 py-0.5 rounded font-mono">
                        {sighting.confidence}% Conf.
                      </span>
                      {sighting.status === 'FLAGGED' && (
                        <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs px-2 py-0.5 rounded font-semibold">
                          FLAGGED
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Live Recognized Number Plates Feed Grid */}
      <div className="bg-dark-panel border border-dark-border rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-dark-border pb-3">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <FileText className="text-emerald-400" size={20} />
            Live ANPR Camera Recognition Log
          </h2>
          <span className="text-xs text-slate-400">Auto-updating live feed</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-slate-900/80 text-xs text-slate-400 uppercase border-b border-dark-border">
              <tr>
                <th className="p-3">Plate Number</th>
                <th className="p-3">Camera Location</th>
                <th className="p-3">Vehicle Type</th>
                <th className="p-3">AI Confidence</th>
                <th className="p-3">Status</th>
                <th className="p-3">Timestamp</th>
                <th className="p-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {plates.length === 0 ? (
                <tr>
                  <td colSpan="7" className="p-6 text-center text-slate-500">
                    No plate recognition events available.
                  </td>
                </tr>
              ) : (
                plates.map((plate) => (
                  <tr key={plate.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="p-3">
                      <span className="font-mono text-white font-bold bg-slate-800 px-2.5 py-1 rounded border border-slate-700">
                        {plate.plate_number}
                      </span>
                    </td>
                    <td className="p-3 font-medium text-slate-200">
                      {plate.camera_name}
                      <span className="block text-xs font-mono text-slate-500">{plate.camera_id}</span>
                    </td>
                    <td className="p-3">{plate.vehicle_type}</td>
                    <td className="p-3">
                      <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded font-mono">
                        {plate.confidence}%
                      </span>
                    </td>
                    <td className="p-3">
                      {plate.status === 'FLAGGED' ? (
                        <span className="bg-rose-500/20 text-rose-400 border border-rose-500/30 text-xs px-2 py-0.5 rounded font-semibold">
                          FLAGGED
                        </span>
                      ) : (
                        <span className="bg-slate-800 text-slate-400 border border-slate-700 text-xs px-2 py-0.5 rounded">
                          NORMAL
                        </span>
                      )}
                    </td>
                    <td className="p-3 text-xs text-slate-400">
                      {new Date(plate.timestamp).toLocaleString()}
                    </td>
                    <td className="p-3 text-right">
                      <button 
                        onClick={() => sampleSearch(plate.plate_number)}
                        className="bg-indigo-600/20 text-indigo-400 border border-indigo-500/30 hover:bg-indigo-600/30 text-xs px-2.5 py-1 rounded transition-colors"
                      >
                        Trace Movement
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ANPR;
