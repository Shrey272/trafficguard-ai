import React, { useState } from 'react';
import { X, Search, Wifi, Check, AlertCircle, RefreshCw, Cpu, Layers, ShieldCheck, ChevronRight, Video, Navigation } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const ONVIFDiscoveryModal = ({ isOpen, onClose, onSelectCameraToRegister }) => {
  const { authFetch } = useAuth();
  const [scanning, setScanning] = useState(false);
  const [devices, setDevices] = useState([]);
  const [error, setError] = useState(null);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [inspecting, setInspecting] = useState(false);
  const [inspectionData, setInspectionData] = useState(null);
  const [selectedProfile, setSelectedProfile] = useState(null);

  if (!isOpen) return null;

  const handleStartScan = async () => {
    setScanning(true);
    setError(null);
    setSelectedDevice(null);
    setInspectionData(null);
    try {
      const res = await authFetch('/api/onvif/discover', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ timeout_seconds: 1.5 })
      });
      if (!res.ok) throw new Error('Discovery scan failed');
      const data = await res.json();
      setDevices(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setScanning(false);
    }
  };

  const handleInspectDevice = async (device) => {
    setSelectedDevice(device);
    setInspecting(true);
    setError(null);
    try {
      const res = await authFetch('/api/onvif/inspect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          host: device.ip_address,
          port: device.port || 80
        })
      });
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Device inspection failed');
      }
      const data = await res.json();
      setInspectionData(data);
      if (data.profiles && data.profiles.length > 0) {
        setSelectedProfile(data.profiles[0]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setInspecting(false);
    }
  };

  const handleRegisterSelected = () => {
    if (!selectedDevice || !inspectionData) return;
    
    const prefill = {
      camera_code: `CAM-ONVIF-${selectedDevice.ip_address.split('.').pop()}`,
      name: `${inspectionData.device_info.manufacturer} ${inspectionData.device_info.model}`,
      vendor: inspectionData.device_info.manufacturer,
      model: inspectionData.device_info.model,
      source_type: 'ONVIF',
      onvif_host: selectedDevice.ip_address,
      onvif_port: selectedDevice.port || 80,
      onvif_profile_token: selectedProfile ? selectedProfile.token : 'Profile_1_Main',
      rtsp_url: selectedProfile ? selectedProfile.stream_uri : inspectionData.default_stream_uri,
      has_ptz: inspectionData.capabilities.ptz,
      capabilities: `STREAMING,ONVIF_PROFILE_S${inspectionData.capabilities.ptz ? ',PTZ' : ''}${inspectionData.capabilities.events ? ',EVENTS' : ''}`,
      location_name: `Network Node ${selectedDevice.ip_address}`,
      latitude: 21.1838 + (Math.random() - 0.5) * 0.02,
      longitude: 72.8223 + (Math.random() - 0.5) * 0.02,
      department: 'Traffic Police',
      vms_name: 'Surat City VMS',
      enabled: true
    };

    onSelectCameraToRegister(prefill);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-dark-panel border border-dark-border rounded-xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl animate-in fade-in zoom-in-95 duration-200">
        
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-cyan-500/10 text-cyan-400 rounded-lg border border-cyan-500/20">
              <Wifi size={22} className={scanning ? 'animate-pulse' : ''} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                ONVIF Device Discovery & Profile Inspector
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  Profile S / T
                </span>
              </h3>
              <p className="text-xs text-slate-400">Discover network CCTV cameras, inspect capabilities & onboard seamlessly</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {/* Action Toolbar */}
        <div className="px-6 py-3 bg-dark-sidebar/60 border-b border-dark-border flex items-center justify-between">
          <div className="text-xs text-slate-300">
            {devices.length > 0 ? (
              <span>Found <strong className="text-cyan-400">{devices.length}</strong> ONVIF transmitters</span>
            ) : (
              <span>Scan local network via WS-Discovery UDP multicast</span>
            )}
          </div>
          <button
            onClick={handleStartScan}
            disabled={scanning}
            className="px-4 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
          >
            <RefreshCw size={14} className={scanning ? 'animate-spin' : ''} />
            <span>{scanning ? 'Probing Subnet...' : 'Discover ONVIF Devices'}</span>
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* Left Column: Discovered Devices List */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Layers size={14} className="text-cyan-400" /> Discovered Hardware ({devices.length})
            </h4>

            {error && (
              <div className="p-3 bg-rose-500/10 border border-rose-500/30 rounded-lg text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle size={15} className="shrink-0" />
                <span>{error}</span>
              </div>
            )}

            {devices.length === 0 && !scanning && (
              <div className="p-8 border border-dashed border-dark-border rounded-xl text-center">
                <Wifi size={32} className="mx-auto text-slate-600 mb-2" />
                <p className="text-sm font-medium text-slate-400">No active discovery probe</p>
                <p className="text-xs text-slate-500 mt-1">Click "Discover ONVIF Devices" above to scan the network.</p>
              </div>
            )}

            {devices.map((dev, idx) => {
              const isSelected = selectedDevice && selectedDevice.ip_address === dev.ip_address;
              return (
                <div
                  key={idx}
                  onClick={() => handleInspectDevice(dev)}
                  className={`p-3.5 rounded-xl border transition-all cursor-pointer ${
                    isSelected 
                      ? 'bg-cyan-950/30 border-cyan-500/50 shadow-lg shadow-cyan-500/5' 
                      : 'bg-dark-panel border-dark-border hover:border-slate-700 hover:bg-slate-800/40'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-sm text-white">{dev.vendor}</span>
                        <span className="text-xs text-slate-400">{dev.model}</span>
                      </div>
                      <div className="text-xs text-cyan-400 font-mono mt-1">
                        {dev.ip_address}:{dev.port}
                      </div>
                    </div>
                    {dev.has_ptz && (
                      <span className="text-[10px] px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 font-medium">
                        PTZ
                      </span>
                    )}
                  </div>

                  <div className="mt-2.5 pt-2.5 border-t border-dark-border/60 flex items-center justify-between text-[11px] text-slate-400">
                    <span>FW: {dev.firmware_version || 'Profile S'}</span>
                    <span className="flex items-center gap-1 text-cyan-300">
                      Inspect Profiles <ChevronRight size={12} />
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Right Column: Device Capabilities & Media Profiles */}
          <div className="space-y-4">
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <Cpu size={14} className="text-blue-400" /> Capabilities & Media Profiles
            </h4>

            {inspecting && (
              <div className="p-12 border border-dark-border rounded-xl text-center bg-dark-sidebar/30">
                <RefreshCw size={28} className="mx-auto text-cyan-400 animate-spin mb-3" />
                <p className="text-sm font-medium text-white">Inspecting ONVIF Services...</p>
                <p className="text-xs text-slate-400 mt-1">Reading device information and media profiles</p>
              </div>
            )}

            {!inspecting && !inspectionData && (
              <div className="p-8 border border-dashed border-dark-border rounded-xl text-center">
                <Video size={32} className="mx-auto text-slate-600 mb-2" />
                <p className="text-sm font-medium text-slate-400">No device selected</p>
                <p className="text-xs text-slate-500 mt-1">Select a discovered camera to inspect media streams.</p>
              </div>
            )}

            {!inspecting && inspectionData && (
              <div className="space-y-4">
                {/* Device Info Card */}
                <div className="p-4 bg-dark-sidebar/70 border border-dark-border rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white">
                      {inspectionData.device_info.manufacturer} {inspectionData.device_info.model}
                    </span>
                    <span className="text-[11px] text-emerald-400 flex items-center gap-1">
                      <ShieldCheck size={13} /> ONVIF Verified
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-400 pt-1">
                    <div>Firmware: <span className="text-slate-200">{inspectionData.device_info.firmware_version}</span></div>
                    <div>Serial: <span className="text-slate-200 font-mono">{inspectionData.device_info.serial_number}</span></div>
                    <div>Hardware: <span className="text-slate-200">{inspectionData.device_info.hardware_id}</span></div>
                    <div>PTZ Control: <span className={inspectionData.capabilities.ptz ? 'text-amber-400 font-semibold' : 'text-slate-400'}>{inspectionData.capabilities.ptz ? 'Enabled' : 'Fixed'}</span></div>
                  </div>
                </div>

                {/* Media Profiles List */}
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-2">
                    Available Stream Profiles ({inspectionData.profiles.length})
                  </label>
                  <div className="space-y-2">
                    {inspectionData.profiles.map((prof, idx) => {
                      const isSelected = selectedProfile && selectedProfile.token === prof.token;
                      return (
                        <div
                          key={idx}
                          onClick={() => setSelectedProfile(prof)}
                          className={`p-3 rounded-lg border cursor-pointer transition-all ${
                            isSelected
                              ? 'bg-blue-950/40 border-blue-500 text-white'
                              : 'bg-dark-sidebar/40 border-dark-border text-slate-300 hover:border-slate-700'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-semibold">{prof.name}</span>
                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-mono">
                              {prof.encoding}
                            </span>
                          </div>
                          <div className="text-[11px] text-slate-400 flex items-center gap-3 mt-1.5">
                            <span>Res: <strong className="text-slate-200">{prof.resolution_width}x{prof.resolution_height}</strong></span>
                            <span>FPS: <strong className="text-slate-200">{prof.framerate}</strong></span>
                            <span>Bitrate: <strong className="text-slate-200">{prof.bitrate_kbps} kbps</strong></span>
                          </div>
                          <div className="text-[10px] text-cyan-400/80 font-mono mt-1 truncate">
                            {prof.stream_uri}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Onboard CTA */}
                <button
                  onClick={handleRegisterSelected}
                  className="w-full py-2.5 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-medium rounded-xl text-sm transition-all shadow-lg shadow-cyan-600/20 flex items-center justify-center gap-2"
                >
                  <Check size={16} />
                  <span>Register Selected ONVIF Camera</span>
                </button>
              </div>
            )}
          </div>

        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-dark-border flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
};

export default ONVIFDiscoveryModal;
