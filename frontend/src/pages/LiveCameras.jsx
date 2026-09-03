import React, { useState, useEffect } from 'react';
import CameraFeed from '../components/ui/CameraFeed';
import { Grid, List, Server, Activity, ArrowRight, Video, RefreshCw } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useRealtime } from '../context/RealtimeContext';

const LiveCameras = () => {
  const { authFetch } = useAuth();
  const { cameraHealthMap } = useRealtime();
  const [cameras, setCameras] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState('ALL');

  useEffect(() => {
    authFetch('/api/cameras')
      .then(res => res.ok ? res.json() : [])
      .then(data => {
        if (Array.isArray(data)) setCameras(data);
      })
      .catch(err => console.error("Error fetching cameras:", err));
  }, []);

  const enrichedCameras = cameras.map(cam => {
    const live = cameraHealthMap[cam.id] || cameraHealthMap[cam.camera_code];
    return {
      ...cam,
      status: live?.status || cam.status,
      fps: live?.fps !== undefined ? live?.fps : cam.fps
    };
  });

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-end gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-2xl font-bold text-white mb-1">Live CCTV Grid</h2>
            <span className="bg-emerald-500/20 text-emerald-400 text-xs px-2 py-0.5 rounded font-mono font-bold">
              AI INGESTION ACTIVE
            </span>
          </div>
          <p className="text-slate-400 text-sm">Real-time RTSP video ingestion and ByteTrack traffic flow analysis.</p>
        </div>
        
        <div className="flex items-center gap-3">
          <Link
            to="/cameras/manage"
            className="px-3.5 py-1.5 bg-blue-600/20 hover:bg-blue-600/30 text-blue-400 border border-blue-500/30 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <Server size={14} />
            <span>Manage Registry</span>
            <ArrowRight size={13} />
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* Large Featured Camera */}
        <div className="lg:col-span-2 flex flex-col h-full">
          <CameraFeed 
            id="CAM-NH48-02" 
            name="Surat-Kadodara Road (NH-48)" 
            type="accident" 
            focus={true}
            className="h-full min-h-[400px]"
            imgSrc="/cam_accident.jpg"
            overlayData={[
              { label: "VEHICLE 1 (COLLISION)", x: "25%", y: "40%", w: "22%", h: "20%", color: "red" },
              { label: "VEHICLE 2 (COLLISION)", x: "48%", y: "40%", w: "24%", h: "22%", color: "red" }
            ]}
          >
            <div className="absolute bottom-4 right-4 text-right text-xs text-white uppercase font-bold tracking-wider">
               <span className="text-rose-500 animate-pulse">●</span> DISPATCH ALERT
            </div>
          </CameraFeed>
        </div>

        {/* Smaller Grid */}
        <div className="grid grid-rows-2 gap-6">
          <CameraFeed 
            id="CAM-RND-03" 
            name="Athwa Gate Circle" 
            imgSrc="/cam_roundabout.jpg"
            overlayData={[
              { label: "CAR (GJ-05-AB)", x: "30%", y: "70%", w: "15%", h: "15%", color: "green" }
            ]}
          />
          <CameraFeed 
            id="CAM-CTY-12" 
            name="Chowk Bazar Heritage Corridor" 
            type="congestion"
            imgSrc="/cam_intersection.jpg"
            overlayData={[
              { label: "CONGESTION: 85%", x: "40%", y: "60%", w: "50%", h: "35%", color: "yellow" }
            ]}
          />
        </div>
      </div>
    </div>
  );
};

export default LiveCameras;
