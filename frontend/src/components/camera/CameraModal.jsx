import React, { useState, useEffect } from 'react';
import { X, Video, MapPin, Shield, Server, Check, AlertCircle, Cpu, Wifi, FileText } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const CameraModal = ({ isOpen, onClose, cameraToEdit, onSave }) => {
  const { authFetch } = useAuth();
  const [formData, setFormData] = useState({
    camera_code: '',
    name: '',
    description: '',
    department: 'Traffic Police',
    vendor: 'Hikvision',
    model: 'DS-2CD2043G2-I',
    vms_name: 'Surat VMS Alpha',
    source_type: 'RTSP',
    location_name: '',
    latitude: 21.1838,
    longitude: 72.8223,
    rtsp_url: '',
    credential_reference: '',
    enabled: true,
    // Phase 2 Fields
    onvif_host: '',
    onvif_port: 80,
    onvif_profile_token: 'Profile_1_Main',
    onvif_username: '',
    onvif_password: '',
    has_ptz: false,
    capabilities: 'STREAMING',
    video_file_path: '',
    device_index: 0
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (cameraToEdit) {
      setFormData({
        camera_code: cameraToEdit.camera_code || '',
        name: cameraToEdit.name || '',
        description: cameraToEdit.description || '',
        department: cameraToEdit.department || 'Traffic Police',
        vendor: cameraToEdit.vendor || 'Hikvision',
        model: cameraToEdit.model || 'Standard IP/PTZ',
        vms_name: cameraToEdit.vms_name || 'Surat VMS Alpha',
        source_type: cameraToEdit.source_type || 'RTSP',
        location_name: cameraToEdit.location_name || '',
        latitude: cameraToEdit.latitude || 21.1838,
        longitude: cameraToEdit.longitude || 72.8223,
        rtsp_url: cameraToEdit.rtsp_url || '',
        credential_reference: cameraToEdit.credential_reference || '',
        enabled: cameraToEdit.enabled !== false,
        onvif_host: cameraToEdit.onvif_host || '',
        onvif_port: cameraToEdit.onvif_port || 80,
        onvif_profile_token: cameraToEdit.onvif_profile_token || 'Profile_1_Main',
        onvif_username: '',
        onvif_password: '',
        has_ptz: cameraToEdit.has_ptz || false,
        capabilities: cameraToEdit.capabilities || 'STREAMING',
        video_file_path: cameraToEdit.video_file_path || '',
        device_index: cameraToEdit.device_index || 0
      });
    } else {
      setFormData({
        camera_code: `CAM-${Math.floor(100 + Math.random() * 900)}`,
        name: '',
        description: '',
        department: 'Traffic Police',
        vendor: 'Hikvision',
        model: 'DS-2CD2043G2-I',
        vms_name: 'Surat VMS Alpha',
        source_type: 'RTSP',
        location_name: '',
        latitude: 21.1838,
        longitude: 72.8223,
        rtsp_url: 'rtsp://admin:pass@192.168.1.100:554/live',
        credential_reference: 'CRED_AUTO_GEN',
        enabled: true,
        onvif_host: '',
        onvif_port: 80,
        onvif_profile_token: 'Profile_1_Main',
        onvif_username: '',
        onvif_password: '',
        has_ptz: false,
        capabilities: 'STREAMING',
        video_file_path: '',
        device_index: 0
      });
    }
    setError(null);
  }, [cameraToEdit, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const url = cameraToEdit && cameraToEdit.id ? `/api/cameras/${cameraToEdit.id}` : '/api/cameras';
      const method = cameraToEdit && cameraToEdit.id ? 'PUT' : 'POST';

      const payload = {
        ...formData,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        onvif_port: parseInt(formData.onvif_port || 80, 10),
        device_index: parseInt(formData.device_index || 0, 10)
      };

      const res = await authFetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: 'Failed to save camera' }));
        throw new Error(errData.detail || 'Failed to save camera');
      }

      const savedCam = await res.json();
      onSave(savedCam);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-dark-panel border border-dark-border rounded-xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
              <Video size={20} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">
                {cameraToEdit && cameraToEdit.id ? 'Edit CCTV Camera' : 'Register New Camera'}
              </h3>
              <p className="text-xs text-slate-400">Configure RTSP stream, ONVIF Profile, VMS gateway & GIS coordinates</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4 overflow-y-auto">
          {error && (
            <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-sm flex items-center gap-2">
              <AlertCircle size={16} className="shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Camera Code */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Camera Code / ID *</label>
              <input
                type="text"
                required
                value={formData.camera_code}
                onChange={e => setFormData({ ...formData, camera_code: e.target.value })}
                placeholder="e.g. CAM-009"
                className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 font-mono"
              />
            </div>

            {/* Camera Name */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Camera Name *</label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={e => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g. Ring Road Overbridge North"
                className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Source Type */}
            <div>
              <label className="block text-xs font-medium text-cyan-400 mb-1">Source Type *</label>
              <select
                value={formData.source_type}
                onChange={e => setFormData({ 
                  ...formData, 
                  source_type: e.target.value,
                  has_ptz: e.target.value === 'ONVIF' ? formData.has_ptz : formData.has_ptz
                })}
                className="w-full bg-dark-sidebar border border-cyan-500/50 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-400 font-medium"
              >
                <option value="RTSP">Live RTSP Stream</option>
                <option value="ONVIF">ONVIF Profile S/T</option>
                <option value="VMS">Enterprise VMS Bridge</option>
                <option value="WEBCAM">USB / Local Webcam</option>
                <option value="FILE">Video File Loop</option>
                <option value="MOCK">Synthetic Stream</option>
              </select>
            </div>

            {/* Department */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Department</label>
              <select
                value={formData.department}
                onChange={e => setFormData({ ...formData, department: e.target.value })}
                className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value="Traffic Police">Traffic Police</option>
                <option value="Municipal Corporation">Municipal Corporation</option>
                <option value="Highway Authority">Highway Authority</option>
                <option value="Smart City Command">Smart City Command</option>
              </select>
            </div>

            {/* Vendor */}
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Vendor / Make</label>
              <select
                value={formData.vendor}
                onChange={e => setFormData({ ...formData, vendor: e.target.value })}
                className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value="Hikvision">Hikvision</option>
                <option value="Dahua">Dahua</option>
                <option value="Axis">Axis Communications</option>
                <option value="Bosch">Bosch Security</option>
                <option value="Uniview">Uniview</option>
                <option value="Hanwha">Hanwha Vision</option>
                <option value="Generic">Generic Video</option>
              </select>
            </div>
          </div>

          {/* Conditional Input: ONVIF Parameters */}
          {formData.source_type === 'ONVIF' && (
            <div className="p-4 bg-cyan-950/20 border border-cyan-500/30 rounded-xl space-y-3">
              <h4 className="text-xs font-semibold text-cyan-300 flex items-center gap-1.5">
                <Wifi size={14} /> ONVIF Device Parameters
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="sm:col-span-2">
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">ONVIF Host IP / Domain *</label>
                  <input
                    type="text"
                    required
                    value={formData.onvif_host}
                    onChange={e => setFormData({ ...formData, onvif_host: e.target.value })}
                    placeholder="192.168.1.120"
                    className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">ONVIF Port</label>
                  <input
                    type="number"
                    value={formData.onvif_port}
                    onChange={e => setFormData({ ...formData, onvif_port: e.target.value })}
                    placeholder="80"
                    className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">Profile Token</label>
                  <input
                    type="text"
                    value={formData.onvif_profile_token}
                    onChange={e => setFormData({ ...formData, onvif_profile_token: e.target.value })}
                    placeholder="Profile_1_Main"
                    className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400 font-mono"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">Device Username</label>
                  <input
                    type="text"
                    value={formData.onvif_username}
                    onChange={e => setFormData({ ...formData, onvif_username: e.target.value })}
                    placeholder="admin"
                    className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-medium text-slate-400 mb-1">Device Password</label>
                  <input
                    type="password"
                    value={formData.onvif_password}
                    onChange={e => setFormData({ ...formData, onvif_password: e.target.value })}
                    placeholder="••••••••"
                    className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-cyan-400"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Conditional Input: Video File */}
          {formData.source_type === 'FILE' && (
            <div className="p-3 bg-amber-950/20 border border-amber-500/30 rounded-xl space-y-2">
              <label className="block text-xs font-medium text-amber-300">Local Video File Path (.mp4, .avi, .mkv)</label>
              <input
                type="text"
                value={formData.video_file_path}
                onChange={e => setFormData({ ...formData, video_file_path: e.target.value })}
                placeholder="videos/traffic_crossing_loop.mp4"
                className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-amber-400 font-mono"
              />
            </div>
          )}

          {/* Conditional Input: USB Webcam */}
          {formData.source_type === 'WEBCAM' && (
            <div className="p-3 bg-emerald-950/20 border border-emerald-500/30 rounded-xl space-y-2">
              <label className="block text-xs font-medium text-emerald-300">USB Device Index (0 for default, 1 for secondary)</label>
              <input
                type="number"
                value={formData.device_index}
                onChange={e => setFormData({ ...formData, device_index: e.target.value })}
                placeholder="0"
                className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-400 font-mono"
              />
            </div>
          )}

          {/* RTSP Stream URL */}
          <div>
            <div className="flex justify-between items-center mb-1">
              <label className="block text-xs font-medium text-slate-300">Stream URI / Direct RTSP Fallback</label>
              <span className="text-[11px] text-slate-400 flex items-center gap-1">
                <Shield size={12} className="text-emerald-400" /> Credentials masked in API
              </span>
            </div>
            <input
              type="text"
              value={formData.rtsp_url}
              onChange={e => setFormData({ ...formData, rtsp_url: e.target.value })}
              placeholder="rtsp://admin:password@192.168.1.100:554/Streaming/Channels/101"
              className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 font-mono text-xs"
            />
          </div>

          {/* Capabilities & PTZ Toggle */}
          <div className="flex items-center gap-6 p-3 bg-dark-sidebar/40 border border-dark-border rounded-xl">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="has_ptz_toggle"
                checked={formData.has_ptz}
                onChange={e => setFormData({ ...formData, has_ptz: e.target.checked })}
                className="w-4 h-4 rounded text-blue-600 bg-dark-sidebar border-dark-border focus:ring-0 cursor-pointer"
              />
              <label htmlFor="has_ptz_toggle" className="text-xs font-medium text-slate-300 cursor-pointer">
                PTZ Enabled (Pan/Tilt/Zoom)
              </label>
            </div>
            <div className="text-[11px] text-slate-400 flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">Profile S</span>
              <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">H.264/H.265</span>
            </div>
          </div>

          {/* GIS Location Details */}
          <div className="border-t border-dark-border pt-4">
            <h4 className="text-xs font-semibold text-slate-300 flex items-center gap-1.5 mb-3">
              <MapPin size={14} className="text-blue-400" /> GIS Geographic Location
            </h4>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-1">
                <label className="block text-xs font-medium text-slate-400 mb-1">Location Name *</label>
                <input
                  type="text"
                  required
                  value={formData.location_name}
                  onChange={e => setFormData({ ...formData, location_name: e.target.value })}
                  placeholder="e.g. Majura Gate Junction"
                  className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Latitude *</label>
                <input
                  type="number"
                  step="0.000001"
                  required
                  value={formData.latitude}
                  onChange={e => setFormData({ ...formData, latitude: e.target.value })}
                  placeholder="21.1838"
                  className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Longitude *</label>
                <input
                  type="number"
                  step="0.000001"
                  required
                  value={formData.longitude}
                  onChange={e => setFormData({ ...formData, longitude: e.target.value })}
                  placeholder="72.8223"
                  className="w-full bg-dark-sidebar border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 font-mono"
                />
              </div>
            </div>
          </div>

          {/* Enabled Switch */}
          <div className="flex items-center gap-3 pt-2">
            <input
              type="checkbox"
              id="enable-camera"
              checked={formData.enabled}
              onChange={e => setFormData({ ...formData, enabled: e.target.checked })}
              className="w-4 h-4 rounded text-blue-600 bg-dark-sidebar border-dark-border focus:ring-0 focus:ring-offset-0 cursor-pointer"
            />
            <label htmlFor="enable-camera" className="text-xs text-slate-300 cursor-pointer font-medium">
              Enable camera stream immediately on normalized adapter gateway
            </label>
          </div>

          {/* Footer Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-dark-border">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
            >
              {saving ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
              ) : (
                <Check size={16} />
              )}
              <span>{cameraToEdit && cameraToEdit.id ? 'Update Camera' : 'Register Camera'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CameraModal;
