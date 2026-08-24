import React from 'react';

const CameraFeed = ({ id, name, type, focus, overlayData, imgSrc, children, className = '' }) => {
  // Determine styles based on type
  const isAlert = type === 'accident';
  const isWarning = type === 'congestion';
  
  const borderColor = isAlert ? 'border-rose-500/50' : isWarning ? 'border-amber-500/50' : 'border-dark-border';
  const statusColor = isAlert ? 'text-rose-400' : isWarning ? 'text-amber-400' : 'text-emerald-400';
  const statusDot = isAlert ? 'bg-rose-500' : isWarning ? 'bg-amber-500' : 'bg-emerald-500';
  
  const statusText = isAlert ? 'ACCIDENT DETECTED' : isWarning ? 'HEAVY TRAFFIC' : 'NORMAL FLOW';

  return (
    <div className={`relative bg-dark-panel border ${borderColor} rounded-lg overflow-hidden flex flex-col ${className}`}>
      {/* Video / Image Area */}
      <div className="relative bg-black flex-1 min-h-[200px] flex items-center justify-center overflow-hidden">
        {/* Actual video feed or placeholder image */}
        <div 
          className="absolute inset-0 opacity-90 bg-cover bg-center" 
          style={{ backgroundImage: `url('${imgSrc || '/cam_highway.jpg'}')` }}
        ></div>
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
        
        {/* Top left badges */}
        <div className="absolute top-3 left-3 flex gap-2 z-10">
          <span className="bg-black/60 backdrop-blur-sm text-slate-200 text-xs px-2 py-1 rounded font-semibold tracking-wider">
            {id}
          </span>
          {isAlert && (
            <span className="bg-rose-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1 font-semibold">
              <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div>
              REC
            </span>
          )}
        </div>

        {/* AI Overlays (passed as children or overlayData) */}
        {overlayData && overlayData.map((box, i) => (
          <div 
            key={i}
            className={`absolute border-2 ${box.color === 'red' ? 'border-rose-500 bg-rose-500/10' : 'border-emerald-400 bg-emerald-400/10'}`}
            style={{ left: box.x, top: box.y, width: box.w, height: box.h }}
          >
            <div className={`absolute -top-6 left-[-2px] px-1 py-0.5 text-[10px] font-bold text-black whitespace-nowrap ${box.color === 'red' ? 'bg-rose-500' : 'bg-emerald-400'}`}>
              {box.label}
            </div>
          </div>
        ))}
        {children}
      </div>

      {/* Footer Details */}
      <div className="p-3 bg-dark-panel flex justify-between items-end">
        <div>
          <h4 className="text-sm font-medium text-slate-200 mb-1">{name}</h4>
          <div className="flex items-center gap-1.5">
            <div className={`w-1.5 h-1.5 rounded-full ${statusDot}`}></div>
            <span className={`text-xs font-semibold ${statusColor}`}>{statusText}</span>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-bold text-white leading-none mb-1">{focus ? '85%' : '32%'}</div>
          <div className="text-[10px] text-slate-500 font-semibold tracking-wider">DENSITY</div>
        </div>
      </div>
    </div>
  );
};

export default CameraFeed;
