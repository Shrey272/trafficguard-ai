import React from 'react';
import StatCard from '../components/ui/StatCard';
import CameraFeed from '../components/ui/CameraFeed';
import { Car, BellRing, Video, Wifi, AlertTriangle, ArrowRight } from 'lucide-react';
import { AreaChart, Area, ResponsiveContainer, XAxis, Tooltip } from 'recharts';
import { useRealtime } from '../context/RealtimeContext';

const chartData = [
  { time: '18:00', density: 85 },
  { time: '18:15', density: 88 },
  { time: '18:30', density: 92 },
  { time: '18:45', density: 95 },
];

const Dashboard = () => {
  const { incidents, lastIncident } = useRealtime();

  const activeAccidents = incidents.filter(i => i.incident_type === 'ACCIDENT' && i.status === 'NEW').length;
  const recentAlerts = incidents.slice(0, 5); // top 5 recent

  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto min-h-full">
      {/* Top Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          title="Active Accidents" 
          value={activeAccidents.toString()} 
          subtext="Unresolved cases" 
          icon={Car}
          valueColor="text-rose-400"
        />
        <StatCard 
          title="Traffic Alerts" 
          value={incidents.length.toString()} 
          subtext="Total logged incidents" 
          icon={BellRing}
          valueColor="text-amber-400"
        />
        <StatCard 
          title="Total Cameras" 
          value="156" 
          subtext="Network capacity: 98%" 
          icon={Video}
        />
        <StatCard 
          title="Online" 
          value="154 / 156" 
          subtext="2 offline for maintenance" 
          icon={Wifi}
          valueColor="text-emerald-400"
        />
      </div>

      {/* Middle Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-[400px]">
        {/* Live Monitoring Grid */}
        <div className="lg:col-span-2 flex flex-col">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <span className="text-blue-500">👁</span> Live Monitoring Area
            </h3>
            <button className="text-xs bg-dark-panel border border-dark-border px-3 py-1.5 rounded-md hover:bg-slate-800 transition-colors">
              AI Vision Active
            </button>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 flex-1">
            <CameraFeed id="CAM-01" name="NH-48 Junction" imgSrc="/cam_highway.jpg" />
            <CameraFeed id="CAM-12" name="City Center" imgSrc="/cam_intersection.jpg" />
            <CameraFeed id="CAM-44" name="Metro Station" imgSrc="/cam_roundabout.jpg" />
            <CameraFeed id="CAM-89" name="North Gate" imgSrc="/cam_night.jpg" />
          </div>
        </div>

        {/* Emergency Alerts Sidebar */}
        <div className="flex flex-col">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-rose-400">
            <AlertTriangle size={20} /> Active Emergency Alerts
            {lastIncident && lastIncident.incident_type === 'ACCIDENT' && (
              <span className="w-2 h-2 rounded-full bg-rose-500 ml-auto animate-pulse"></span>
            )}
          </h3>
          <div className="flex-1 space-y-4 overflow-y-auto max-h-[350px] pr-2 custom-scrollbar">
            {recentAlerts.map(alert => (
              alert.incident_type === 'ACCIDENT' ? (
                <div key={alert.id} className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-4 relative overflow-hidden">
                  <div className="absolute top-0 left-0 w-1 h-full bg-rose-500"></div>
                  <div className="flex justify-between items-start mb-4">
                    <span className="bg-rose-500 text-white text-xs px-2 py-0.5 rounded font-bold tracking-wider">
                      {alert.severity.toUpperCase()} ACCIDENT
                    </span>
                    <span className="text-xs text-rose-300">
                      {new Date(alert.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </span>
                  </div>
                  <div className="space-y-2 text-sm mb-4">
                    <div className="flex justify-between"><span className="text-slate-400">LOCATION</span><span className="text-white">{alert.camera_id}</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">CONFIDENCE</span><span className="text-rose-400 font-bold">{alert.confidence}%</span></div>
                    <div className="flex justify-between"><span className="text-slate-400">VEHICLES INVOLVED</span><span className="text-white">{alert.vehicle_count}</span></div>
                  </div>
                  <div className="flex gap-2">
                    <button className="flex-1 bg-rose-500/20 text-rose-400 py-2 rounded font-semibold text-sm hover:bg-rose-500/30 transition-colors">View</button>
                    <button className="flex-1 bg-dark-panel border border-rose-500/30 py-2 rounded font-semibold text-sm hover:bg-slate-800 transition-colors">Ack</button>
                  </div>
                </div>
              ) : (
                <div key={alert.id} className="bg-dark-panel border border-dark-border rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <span className="text-amber-400 text-sm font-semibold flex items-center gap-1.5"><AlertTriangle size={14}/> {alert.severity.toUpperCase()} CONGESTION</span>
                    <span className="text-xs text-slate-500">
                      {new Date(alert.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </span>
                  </div>
                  <div className="text-sm text-slate-300 mb-1">{alert.camera_id}</div>
                  <div className="text-xs text-slate-500">Conf: {alert.confidence}%</div>
                </div>
              )
            ))}
            {recentAlerts.length === 0 && (
              <div className="text-slate-500 text-sm text-center py-4">No recent alerts</div>
            )}
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 pb-6">
        <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
          <h3 className="text-base font-semibold mb-4 text-white">Live Traffic Trends</h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorDensity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" stroke="#475569" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip contentStyle={{ backgroundColor: '#1a1e2b', borderColor: '#2a2f42' }} />
                <Area type="monotone" dataKey="density" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#colorDensity)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
          <h3 className="text-base font-semibold mb-4 text-white">Recent Incidents Log</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs text-slate-500 uppercase border-b border-dark-border">
                <tr>
                  <th className="pb-3 font-medium">Time</th>
                  <th className="pb-3 font-medium">Type</th>
                  <th className="pb-3 font-medium">Location</th>
                  <th className="pb-3 font-medium">Status</th>
                </tr>
              </thead>
              <tbody className="text-slate-300">
                {incidents.slice(0, 4).map(inc => (
                  <tr key={inc.id} className="border-b border-dark-border/50">
                    <td className="py-3">{new Date(inc.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                    <td className={`py-3 ${inc.incident_type === 'ACCIDENT' ? 'text-rose-400' : 'text-amber-400'}`}>
                      {inc.incident_type === 'ACCIDENT' ? `Accident (${inc.severity})` : `Congestion (${inc.severity})`}
                    </td>
                    <td className="py-3">{inc.camera_id}</td>
                    <td className="py-3">
                      <span className={`border px-2 py-1 rounded text-xs font-medium ${
                        inc.status === 'NEW' ? 'border-rose-500/50 text-rose-400' : 'border-amber-500/50 text-amber-400'
                      }`}>
                        {inc.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
