import React from 'react';
import CameraFeed from '../components/ui/CameraFeed';
import { Grid, List } from 'lucide-react';

const LiveCameras = () => {
  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">Live CCTV Grid</h2>
          <p className="text-slate-400 text-sm">Real-time AI object detection and traffic flow analysis.</p>
        </div>
        
        <div className="flex items-center gap-4 bg-dark-panel border border-dark-border p-1.5 rounded-lg">
          <div className="flex gap-1 border-r border-dark-border pr-3">
            <button className="px-4 py-1.5 bg-slate-800 text-white rounded text-sm font-medium">All Cameras (24)</button>
            <button className="px-4 py-1.5 text-slate-400 hover:text-white rounded text-sm transition-colors">Normal (18)</button>
            <button className="px-4 py-1.5 text-slate-400 hover:text-white rounded text-sm transition-colors">Heavy Traffic (5)</button>
            <button className="px-4 py-1.5 flex items-center gap-2 text-rose-400 hover:bg-rose-500/10 rounded text-sm transition-colors">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500"></span> Accident Detected (1)
            </button>
          </div>
          <div className="flex gap-2 px-2 text-slate-400">
            <button className="p-1 hover:text-white"><List size={18} /></button>
            <button className="p-1 text-white bg-slate-800 rounded"><Grid size={18} /></button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* Large Featured Camera */}
        <div className="lg:col-span-2">
          <CameraFeed 
            id="CAM-NH48-02" 
            name="NH-48 Junction" 
            type="accident" 
            focus={true}
            imgSrc="/cam_highway.jpg"
            overlayData={[
              { label: "VEHICLE 1 (0V)", x: "20%", y: "45%", w: "30%", h: "20%", color: "red" },
              { label: "VEHICLE 2 (0V)", x: "45%", y: "40%", w: "25%", h: "25%", color: "red" }
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
            name="Central Roundabout" 
            imgSrc="/cam_roundabout.jpg"
            overlayData={[
              { label: "CAR", x: "30%", y: "70%", w: "15%", h: "15%", color: "green" }
            ]}
          />
          <CameraFeed 
            id="CAM-CTY-12" 
            name="City Center 5th Ave" 
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
