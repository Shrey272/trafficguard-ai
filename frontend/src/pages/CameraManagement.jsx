import React, { useState, useEffect } from 'react';
import { 
  Video, Plus, Search, Filter, RefreshCw, Power, Play, Square, 
  Trash2, Edit3, Shield, MapPin, Activity, CheckCircle2, AlertTriangle, 
  XCircle, Clock, Server, Eye, Wifi, Navigation, Layers
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';
import CameraModal from '../components/camera/CameraModal';
import ONVIFDiscoveryModal from '../components/camera/ONVIFDiscoveryModal';

const CameraManagement = () => {
  const { authFetch, isAdmin, isOperator, user } = useAuth();
  const { cameraHealthMap } = useRealtime();

  const [cameras, setCameras] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedSourceType, setSelectedSourceType] = useState('ALL');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDiscoveryOpen, setIsDiscoveryOpen] = useState(false);
  const [cameraToEdit, setCameraToEdit] = useState(null);
  const [actionLoadingId, setActionLoadingId] = useState(null);
  const [notification, setNotification] = useState(null);

  const fetchCameras = async () => {
    try {
      setLoading(true);
      const res = await authFetch('/api/cameras');
      if (res.ok) {
        const data = await res.json();
        setCameras(data);
      }
    } catch (err) {
      console.error("Failed to load cameras:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCameras();
  }, []);

  const showNotification = (msg, type = 'success') => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 4000);
  };

  const handleConnect = async (camId) => {
    try {
      setActionLoadingId(camId);
      const res = await authFetch(`/api/cameras/${camId}/connect`, { method: 'POST' });
      if (res.ok) {
        showNotification(`Connected stream for ${camId}`);
        fetchCameras();
      } else {
        const err = await res.json();
        showNotification(err.detail || 'Failed to connect stream', 'error');
      }
    } catch (e) {
      showNotification(e.message, 'error');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDisconnect = async (camId) => {
    try {
      setActionLoadingId(camId);
      const res = await authFetch(`/api/cameras/${camId}/disconnect`, { method: 'POST' });
      if (res.ok) {
        showNotification(`Disconnected stream for ${camId}`);
        fetchCameras();
      } else {
        const err = await res.json();
        showNotification(err.detail || 'Failed to disconnect stream', 'error');
      }
    } catch (e) {
      showNotification(e.message, 'error');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleRestart = async (camId) => {
    try {
      setActionLoadingId(camId);
      const res = await authFetch(`/api/cameras/${camId}/restart`, { method: 'POST' });
      if (res.ok) {
        showNotification(`Restarted stream for ${camId}`);
        fetchCameras();
      } else {
        const err = await res.json();
        showNotification(err.detail || 'Failed to restart stream', 'error');
      }
    } catch (e) {
      showNotification(e.message, 'error');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleDelete = async (cam) => {
    if (!window.confirm(`Are you sure you want to permanently delete camera ${cam.camera_code} (${cam.name})?`)) {
      return;
    }
    try {
      setActionLoadingId(cam.id);
      const res = await authFetch(`/api/cameras/${cam.id}`, { method: 'DELETE' });
      if (res.ok) {
        showNotification(`Camera ${cam.camera_code} deleted successfully`);
        setCameras(prev => prev.filter(c => c.id !== cam.id));
      } else {
        const err = await res.json();
        showNotification(err.detail || 'Failed to delete camera', 'error');
      }
    } catch (e) {
      showNotification(e.message, 'error');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleRegisterFromDiscovery = (prefillData) => {
    setCameraToEdit(prefillData);
    setIsModalOpen(true);
  };

  // Merge live health data from WebSocket
  const enrichedCameras = cameras.map(cam => {
    const liveHealth = cameraHealthMap[cam.id] || cameraHealthMap[cam.camera_code];
    if (liveHealth) {
      return {
        ...cam,
        status: liveHealth.status || cam.status,
        fps: liveHealth.fps !== undefined ? liveHealth.fps : cam.fps,
        latency_ms: liveHealth.latency_ms !== undefined ? liveHealth.latency_ms : cam.latency_ms,
        has_ptz: liveHealth.has_ptz !== undefined ? liveHealth.has_ptz : cam.has_ptz
      };
    }
    return cam;
  });

  const filteredCameras = enrichedCameras.filter(cam => {
    const matchesSearch = 
      cam.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cam.camera_code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cam.location_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cam.department?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cam.vendor?.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesDept = selectedDept === 'ALL' || cam.department === selectedDept;
    const matchesStatus = selectedStatus === 'ALL' || cam.status === selectedStatus;
    const matchesSource = selectedSourceType === 'ALL' || (cam.source_type || 'RTSP').toUpperCase() === selectedSourceType;

    return matchesSearch && matchesDept && matchesStatus && matchesSource;
  });

  const stats = {
    total: cameras.length,
    online: enrichedCameras.filter(c => c.status === 'ONLINE').length,
    connecting: enrichedCameras.filter(c => c.status === 'CONNECTING').length,
    offline: enrichedCameras.filter(c => c.status === 'OFFLINE' || c.status === 'DISABLED').length,
    error: enrichedCameras.filter(c => c.status === 'ERROR').length,
    onvifCount: enrichedCameras.filter(c => c.source_type === 'ONVIF').length
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'ONLINE':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> ONLINE
          </span>
        );
      case 'CONNECTING':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span> CONNECTING
          </span>
        );
      case 'ERROR':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <span className="w-2 h-2 rounded-full bg-rose-500"></span> ERROR
          </span>
        );
      case 'DISABLED':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <Square size={8} className="fill-slate-400" /> DISABLED
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-800 text-slate-400 border border-slate-700">
            <span className="w-2 h-2 rounded-full bg-slate-500"></span> OFFLINE
          </span>
        );
    }
  };

  const getSourceBadge = (sourceType, hasPtz) => {
    const st = (sourceType || 'RTSP').toUpperCase();
    let bg = 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    if (st === 'ONVIF') bg = 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
    if (st === 'FILE') bg = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
    if (st === 'WEBCAM') bg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    if (st === 'VMS') bg = 'bg-purple-500/10 text-purple-400 border-purple-500/20';

    return (
      <div className="flex items-center gap-1.5">
        <span className={`text-[10px] font-mono px-2 py-0.5 rounded border font-semibold ${bg}`}>
          {st}
        </span>
        {hasPtz && (
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-500/15 text-amber-300 border border-amber-500/30 font-semibold" title="PTZ Control Enabled">
            PTZ
          </span>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full">
      {/* Header & Stats Banner */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h2 className="text-2xl font-bold text-white">CCTV Integration Gateway</h2>
            <span className="bg-slate-800 text-slate-300 text-xs px-2.5 py-1 rounded-md font-mono border border-dark-border">
              RBAC: {user?.role || 'VIEWER'}
            </span>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Normalized CCTV & VMS Gateway: ONVIF Profile S/T, RTSP, Video Files, USB Devices, and Enterprise VMS.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchCameras}
            className="p-2 bg-dark-panel border border-dark-border text-slate-300 hover:text-white rounded-lg transition-colors"
            title="Refresh Registry"
          >
            <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
          </button>

          {/* ONVIF Discovery Button (Admin & Operator) */}
          {(isAdmin || isOperator) && (
            <button
              onClick={() => setIsDiscoveryOpen(true)}
              className="px-3.5 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-sm font-medium transition-all flex items-center gap-2 shadow-lg shadow-cyan-500/20"
            >
              <Wifi size={17} className="animate-pulse text-cyan-200" />
              <span>Discover ONVIF</span>
            </button>
          )}

          {isAdmin ? (
            <button
              onClick={() => {
                setCameraToEdit(null);
                setIsModalOpen(true);
              }}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 shadow-lg shadow-blue-600/20"
            >
              <Plus size={18} />
              <span>Register Camera</span>
            </button>
          ) : (
            <div className="text-xs text-slate-400 bg-dark-panel border border-dark-border px-3 py-2 rounded-lg flex items-center gap-1.5">
              <Shield size={14} className="text-amber-400" />
              <span>Admin permission required to add cameras</span>
            </div>
          )}
        </div>
      </div>

      {/* Notification Toast */}
      {notification && (
        <div className={`p-3 rounded-lg text-sm flex items-center gap-2 animate-in fade-in slide-in-from-top-2 ${
          notification.type === 'error' 
            ? 'bg-rose-500/10 border border-rose-500/30 text-rose-400' 
            : 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400'
        }`}>
          {notification.type === 'error' ? <AlertTriangle size={16} /> : <CheckCircle2 size={16} />}
          <span>{notification.msg}</span>
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        <div className="bg-dark-panel border border-dark-border rounded-xl p-3.5 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">Total Gateway Streams</p>
            <p className="text-xl font-bold text-white mt-0.5">{stats.total}</p>
          </div>
          <div className="p-2.5 bg-blue-500/10 text-blue-400 rounded-lg">
            <Video size={20} />
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-xl p-3.5 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">Online & Active</p>
            <p className="text-xl font-bold text-emerald-400 mt-0.5">{stats.online}</p>
          </div>
          <div className="p-2.5 bg-emerald-500/10 text-emerald-400 rounded-lg">
            <CheckCircle2 size={20} />
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-xl p-3.5 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">ONVIF / VMS Nodes</p>
            <p className="text-xl font-bold text-cyan-400 mt-0.5">{stats.onvifCount}</p>
          </div>
          <div className="p-2.5 bg-cyan-500/10 text-cyan-400 rounded-lg">
            <Wifi size={20} />
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-xl p-3.5 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">Stream Errors</p>
            <p className="text-xl font-bold text-rose-400 mt-0.5">{stats.error}</p>
          </div>
          <div className="p-2.5 bg-rose-500/10 text-rose-400 rounded-lg">
            <AlertTriangle size={20} />
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-xl p-3.5 flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-400">Offline / Disabled</p>
            <p className="text-xl font-bold text-slate-400 mt-0.5">{stats.offline}</p>
          </div>
          <div className="p-2.5 bg-slate-800 text-slate-400 rounded-lg">
            <XCircle size={20} />
          </div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="bg-dark-panel border border-dark-border rounded-xl p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="Search code, name, vendor, location..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className="w-full bg-dark-sidebar border border-dark-border rounded-lg pl-9 pr-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 placeholder-slate-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          {/* Source Type Filter */}
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Protocol:</span>
            <select
              value={selectedSourceType}
              onChange={e => setSelectedSourceType(e.target.value)}
              className="bg-dark-sidebar border border-cyan-500/40 rounded-lg px-2.5 py-1.5 text-xs text-cyan-300 focus:outline-none focus:border-cyan-400 font-medium"
            >
              <option value="ALL">All Protocols</option>
              <option value="RTSP">RTSP</option>
              <option value="ONVIF">ONVIF Profile S/T</option>
              <option value="VMS">Enterprise VMS</option>
              <option value="WEBCAM">USB Webcam</option>
              <option value="FILE">Video File</option>
            </select>
          </div>

          {/* Department Filter */}
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Dept:</span>
            <select
              value={selectedDept}
              onChange={e => setSelectedDept(e.target.value)}
              className="bg-dark-sidebar border border-dark-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Departments</option>
              <option value="Traffic Police">Traffic Police</option>
              <option value="Municipal Corporation">Municipal Corporation</option>
              <option value="Highway Authority">Highway Authority</option>
              <option value="Smart City Command">Smart City Command</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>Status:</span>
            <select
              value={selectedStatus}
              onChange={e => setSelectedStatus(e.target.value)}
              className="bg-dark-sidebar border border-dark-border rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none focus:border-blue-500"
            >
              <option value="ALL">All Statuses</option>
              <option value="ONLINE">Online</option>
              <option value="CONNECTING">Connecting</option>
              <option value="ERROR">Error</option>
              <option value="OFFLINE">Offline</option>
              <option value="DISABLED">Disabled</option>
            </select>
          </div>
        </div>
      </div>

      {/* Cameras Table */}
      <div className="bg-dark-panel border border-dark-border rounded-xl overflow-hidden flex-1 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-dark-sidebar border-b border-dark-border text-xs text-slate-400 uppercase tracking-wider font-semibold">
              <tr>
                <th className="px-4 py-3.5">Status</th>
                <th className="px-4 py-3.5">Protocol & Source</th>
                <th className="px-4 py-3.5">Camera / Make</th>
                <th className="px-4 py-3.5">Department & VMS</th>
                <th className="px-4 py-3.5">GIS Location</th>
                <th className="px-4 py-3.5 text-center">Telemetry</th>
                <th className="px-4 py-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-dark-border">
              {filteredCameras.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-12 text-center text-slate-500">
                    {loading ? "Loading integration gateway..." : "No cameras match your search criteria."}
                  </td>
                </tr>
              ) : (
                filteredCameras.map((cam) => {
                  const isLoadingAction = actionLoadingId === cam.id;
                  return (
                    <tr key={cam.id} className="hover:bg-slate-800/30 transition-colors">
                      {/* Status */}
                      <td className="px-4 py-3.5 whitespace-nowrap">
                        {getStatusBadge(cam.status)}
                      </td>

                      {/* Source Type & Protocol */}
                      <td className="px-4 py-3.5 whitespace-nowrap">
                        {getSourceBadge(cam.source_type, cam.has_ptz)}
                        <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                          {cam.source_type === 'ONVIF' ? (cam.onvif_host || 'ONVIF S') : 'Gateway'}
                        </div>
                      </td>

                      {/* Camera Info */}
                      <td className="px-4 py-3.5">
                        <div className="font-semibold text-white flex items-center gap-2">
                          <span className="font-mono text-blue-400 text-xs px-1.5 py-0.5 bg-blue-500/10 rounded border border-blue-500/20">
                            {cam.camera_code}
                          </span>
                          <span>{cam.name}</span>
                        </div>
                        <div className="text-xs text-slate-400 mt-0.5">
                          {cam.vendor} • {cam.model}
                        </div>
                      </td>

                      {/* Department & VMS */}
                      <td className="px-4 py-3.5">
                        <div className="text-xs font-medium text-slate-200">{cam.department}</div>
                        <div className="text-[11px] text-slate-400 mt-0.5 flex items-center gap-1">
                          <Server size={11} className="text-slate-500" /> {cam.vms_name || 'Surat VMS'}
                        </div>
                      </td>

                      {/* GIS Location */}
                      <td className="px-4 py-3.5">
                        <div className="text-xs text-slate-200 flex items-center gap-1 font-medium">
                          <MapPin size={12} className="text-rose-400 shrink-0" />
                          <span>{cam.location_name}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 font-mono mt-0.5">
                          {cam.latitude?.toFixed(4)}, {cam.longitude?.toFixed(4)}
                        </div>
                      </td>

                      {/* Telemetry (FPS / Latency) */}
                      <td className="px-4 py-3.5 text-center whitespace-nowrap">
                        <div className="text-xs font-mono text-emerald-400 font-semibold">
                          {cam.fps ? `${cam.fps.toFixed(1)} FPS` : (cam.status === 'ONLINE' ? '25.0 FPS' : '0.0 FPS')}
                        </div>
                        <div className="text-[11px] text-slate-400 flex items-center justify-center gap-1 mt-0.5">
                          <Clock size={10} />
                          <span>{cam.last_seen ? new Date(cam.last_seen).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Live'}</span>
                        </div>
                      </td>

                      {/* Actions */}
                      <td className="px-4 py-3.5 text-right whitespace-nowrap">
                        <div className="flex items-center justify-end gap-1.5">
                          {/* Connect / Disconnect */}
                          {isOperator && (
                            <>
                              {cam.status === 'ONLINE' ? (
                                <button
                                  onClick={() => handleDisconnect(cam.id)}
                                  disabled={isLoadingAction}
                                  title="Disconnect Stream"
                                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-rose-400 rounded-lg transition-colors disabled:opacity-50"
                                >
                                  <Power size={15} />
                                </button>
                              ) : (
                                <button
                                  onClick={() => handleConnect(cam.id)}
                                  disabled={isLoadingAction}
                                  title="Connect Stream"
                                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 rounded-lg transition-colors disabled:opacity-50"
                                >
                                  <Play size={15} />
                                </button>
                              )}

                              {/* Restart */}
                              <button
                                onClick={() => handleRestart(cam.id)}
                                disabled={isLoadingAction}
                                title="Restart Stream Adapter"
                                className="p-1.5 bg-slate-800 hover:bg-slate-700 text-amber-400 rounded-lg transition-colors disabled:opacity-50"
                              >
                                <RefreshCw size={15} className={isLoadingAction ? 'animate-spin' : ''} />
                              </button>
                            </>
                          )}

                          {/* Admin Edit & Delete */}
                          {isAdmin && (
                            <>
                              <button
                                onClick={() => {
                                  setCameraToEdit(cam);
                                  setIsModalOpen(true);
                                }}
                                title="Edit Camera Metadata"
                                className="p-1.5 bg-slate-800 hover:bg-slate-700 text-blue-400 rounded-lg transition-colors"
                              >
                                <Edit3 size={15} />
                              </button>

                              <button
                                onClick={() => handleDelete(cam)}
                                disabled={isLoadingAction}
                                title="Delete Camera"
                                className="p-1.5 bg-slate-800 hover:bg-rose-500/20 text-rose-400 rounded-lg transition-colors disabled:opacity-50"
                              >
                                <Trash2 size={15} />
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Camera Edit / Register Modal */}
      <CameraModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setCameraToEdit(null);
        }}
        cameraToEdit={cameraToEdit}
        onSave={() => {
          showNotification(cameraToEdit && cameraToEdit.id ? 'Camera updated successfully' : 'Camera registered successfully');
          fetchCameras();
        }}
      />

      {/* ONVIF Discovery Wizard Modal */}
      <ONVIFDiscoveryModal
        isOpen={isDiscoveryOpen}
        onClose={() => setIsDiscoveryOpen(false)}
        onSelectCameraToRegister={handleRegisterFromDiscovery}
      />
    </div>
  );
};

export default CameraManagement;
