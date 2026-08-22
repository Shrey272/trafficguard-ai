import React from 'react';
import { Car, ShieldAlert, AlertTriangle, Calendar, Download, TrendingUp, TrendingDown, ArrowRight } from 'lucide-react';
import { BarChart, Bar, ResponsiveContainer, XAxis, Tooltip, CartesianGrid, Legend } from 'recharts';

const trafficData = [
  { time: '06:00', Cars: 6200, Bikes: 2500, Trucks: 1200 },
  { time: '09:00', Cars: 12100, Bikes: 3800, Trucks: 4900 },
  { time: '12:00', Cars: 8900, Bikes: 3200, Trucks: 3800 },
  { time: '15:00', Cars: 7500, Bikes: 2600, Trucks: 4500 },
  { time: '18:00', Cars: 12800, Bikes: 4200, Trucks: 2500 },
  { time: '21:00', Cars: 5100, Bikes: 1200, Trucks: 1800 },
];

const Analytics = () => {
  return (
    <div className="flex flex-col gap-6 max-w-7xl mx-auto h-full">
      {/* Header */}
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-white mb-1">Long-term Analytics</h2>
          <p className="text-slate-400 text-sm">System performance and network health over the last 30 days.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 bg-dark-panel border border-dark-border text-slate-300 px-4 py-2 rounded-lg text-sm hover:bg-slate-800 transition-colors">
            <Calendar size={16} /> Last 30 Days
          </button>
          <button className="flex items-center gap-2 bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-500/30 transition-colors">
            <Download size={16} /> Export
          </button>
        </div>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-white font-medium">Peak Hour Traffic</h3>
            <div className="text-blue-500 bg-blue-500/10 p-2 rounded"><Car size={18} /></div>
          </div>
          <div className="flex items-baseline gap-3 mb-1">
            <div className="text-4xl font-bold text-white">14.2k</div>
            <div className="flex items-center text-emerald-400 text-sm font-semibold"><TrendingDown size={14} className="mr-1"/> 2.1%</div>
          </div>
          <div className="text-sm text-slate-500">Avg. vehicles / hour at 17:00</div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-white font-medium">Incident Reduction</h3>
            <div className="text-emerald-500 bg-emerald-500/10 p-2 rounded"><ShieldAlert size={18} /></div>
          </div>
          <div className="flex items-baseline gap-3 mb-1">
            <div className="text-4xl font-bold text-emerald-400">18%</div>
            <div className="flex items-center text-emerald-400 text-sm font-semibold"><TrendingUp size={14} className="mr-1"/> YoY</div>
          </div>
          <div className="text-sm text-slate-500">Compared to previous month</div>
        </div>

        <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
          <div className="flex justify-between items-start mb-4">
            <h3 className="text-white font-medium">Network Anomalies</h3>
            <div className="text-rose-500 bg-rose-500/10 p-2 rounded"><AlertTriangle size={18} /></div>
          </div>
          <div className="flex items-baseline gap-3 mb-1">
            <div className="text-4xl font-bold text-rose-400">24</div>
            <div className="flex items-center text-rose-400 text-sm font-semibold"><TrendingUp size={14} className="mr-1"/> 4</div>
          </div>
          <div className="text-sm text-slate-500">Unresolved major congestion alerts</div>
        </div>
      </div>

      {/* Main Chart */}
      <div className="bg-dark-panel border border-dark-border rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-6">Traffic Volume by Hour</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trafficData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2a2f42" vertical={false} />
              <XAxis dataKey="time" stroke="#475569" fontSize={12} tickLine={false} axisLine={false} dy={10} />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1a1e2b', borderColor: '#2a2f42', color: '#fff' }}
                itemStyle={{ color: '#fff' }}
                cursor={{ fill: '#121621' }}
              />
              <Legend verticalAlign="top" align="right" iconType="circle" wrapperStyle={{ paddingBottom: '20px', fontSize: '12px' }} />
              <Bar dataKey="Cars" fill="#93c5fd" radius={[2, 2, 0, 0]} barSize={12} />
              <Bar dataKey="Bikes" fill="#34d399" radius={[2, 2, 0, 0]} barSize={12} />
              <Bar dataKey="Trucks" fill="#94a3b8" radius={[2, 2, 0, 0]} barSize={12} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 pb-6">
        {/* Hotspots */}
        <div className="bg-dark-panel border border-dark-border rounded-lg p-5 flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-base font-semibold text-white">Congestion Hotspots</h3>
            <button className="text-slate-500 hover:text-white">•••</button>
          </div>
          <div className="space-y-6 flex-1 justify-center flex flex-col">
            <div>
              <div className="flex justify-between text-sm mb-1.5"><span className="text-slate-300">I-95 North</span><span className="text-rose-400 font-semibold">85%</span></div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-rose-400 rounded-full" style={{width: '85%'}}></div></div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1.5"><span className="text-slate-300">Downtown Ext</span><span className="text-amber-400 font-semibold">62%</span></div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-amber-400 rounded-full" style={{width: '62%'}}></div></div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1.5"><span className="text-slate-300">Route 66</span><span className="text-indigo-400 font-semibold">45%</span></div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-indigo-400 rounded-full" style={{width: '45%'}}></div></div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1.5"><span className="text-slate-300">Bridge Port</span><span className="text-emerald-400 font-semibold">20%</span></div>
              <div className="h-2 w-full bg-slate-800 rounded-full overflow-hidden"><div className="h-full bg-emerald-400 rounded-full" style={{width: '20%'}}></div></div>
            </div>
          </div>
        </div>

        {/* Accident Frequency - Mock UI */}
        <div className="bg-dark-panel border border-dark-border rounded-lg p-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-base font-semibold text-white">Accident Frequency by Day</h3>
            <BarChart size={16} className="text-slate-500" />
          </div>
          <div className="h-32 border border-dark-border/50 rounded flex items-end justify-between p-4 relative">
             <div className="absolute inset-0 bg-slate-800/10" style={{ backgroundSize: '100% 20px', backgroundImage: 'linear-gradient(to bottom, transparent 19px, #2a2f42 20px)' }}></div>
             <div className="z-10 flex flex-col items-center gap-2"><div className="w-1.5 h-12 bg-slate-600 rounded-t"></div><span className="text-[10px] text-slate-500">Mon</span></div>
             <div className="z-10 flex flex-col items-center gap-2"><div className="w-1.5 h-16 bg-slate-600 rounded-t"></div><span className="text-[10px] text-slate-500">Tue</span></div>
             <div className="z-10 flex flex-col items-center gap-2"><div className="w-1.5 h-8 bg-slate-600 rounded-t"></div><span className="text-[10px] text-slate-500">Wed</span></div>
             <div className="z-10 flex flex-col items-center gap-2"><div className="w-1.5 h-20 bg-slate-600 rounded-t"></div><span className="text-[10px] text-slate-500">Thu</span></div>
             <div className="z-10 flex flex-col items-center gap-2"><div className="w-1.5 h-24 bg-rose-400 rounded-t shadow-[0_0_8px_rgba(251,113,133,0.5)]"></div><span className="text-[10px] text-rose-400 font-bold">Fri</span></div>
             <div className="z-10 flex flex-col items-center gap-2"><div className="w-1.5 h-14 bg-slate-600 rounded-t"></div><span className="text-[10px] text-slate-500">Sat</span></div>
             <div className="z-10 flex flex-col items-center gap-2"><div className="w-1.5 h-10 bg-slate-600 rounded-t"></div><span className="text-[10px] text-slate-500">Sun</span></div>
          </div>
        </div>

        {/* Top 5 Locations */}
        <div className="lg:col-span-3 bg-dark-panel border border-dark-border rounded-lg p-5">
           <div className="flex justify-between items-center mb-4">
              <h3 className="text-base font-semibold text-white">Top 5 Most Congested Locations</h3>
              <button className="text-xs text-indigo-400 hover:text-indigo-300 font-medium">View All Map Data</button>
           </div>
           <div className="overflow-x-auto">
              <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="text-[10px] text-slate-500 uppercase border-b border-dark-border">
                  <tr>
                    <th className="pb-3 font-medium">Location ID / Name</th>
                    <th className="pb-3 font-medium">Severity</th>
                    <th className="pb-3 font-medium">Avg. Delay</th>
                    <th className="pb-3 font-medium">Peak Hours</th>
                    <th className="pb-3 font-medium text-right">Trend (7d)</th>
                  </tr>
                </thead>
                <tbody className="text-slate-300">
                  <tr className="border-b border-dark-border/50">
                    <td className="py-3 flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span> I-95 North, Mile 42</td>
                    <td className="py-3"><span className="border border-rose-500/50 text-rose-400 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider">CRITICAL</span></td>
                    <td className="py-3 font-medium">45 mins</td>
                    <td className="py-3 text-slate-400 text-xs">07:00 - 09:30</td>
                    <td className="py-3 text-right"><TrendingUp size={16} className="text-rose-400 inline" /></td>
                  </tr>
                  <tr className="border-b border-dark-border/50">
                    <td className="py-3 flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span> Downtown Exit 4A</td>
                    <td className="py-3"><span className="border border-amber-500/50 text-amber-400 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider">HIGH</span></td>
                    <td className="py-3 font-medium">28 mins</td>
                    <td className="py-3 text-slate-400 text-xs">16:30 - 18:45</td>
                    <td className="py-3 text-right"><ArrowRight size={16} className="text-slate-500 inline" /></td>
                  </tr>
                  <tr className="border-b border-dark-border/50">
                    <td className="py-3 flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span> West Blvd Intersection</td>
                    <td className="py-3"><span className="border border-amber-500/50 text-amber-400 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider">HIGH</span></td>
                    <td className="py-3 font-medium">22 mins</td>
                    <td className="py-3 text-slate-400 text-xs">17:00 - 18:00</td>
                    <td className="py-3 text-right"><TrendingUp size={16} className="text-rose-400 inline" /></td>
                  </tr>
                  <tr className="border-b border-dark-border/50">
                    <td className="py-3 flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span> Route 66, Section B</td>
                    <td className="py-3"><span className="border border-indigo-500/50 text-indigo-400 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider">MODERATE</span></td>
                    <td className="py-3 font-medium">15 mins</td>
                    <td className="py-3 text-slate-400 text-xs">08:00 - 09:00</td>
                    <td className="py-3 text-right"><TrendingDown size={16} className="text-emerald-400 inline" /></td>
                  </tr>
                  <tr>
                    <td className="py-3 flex items-center gap-2"><span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span> Bridge Port Tunnel</td>
                    <td className="py-3"><span className="border border-indigo-500/50 text-indigo-400 px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider">MODERATE</span></td>
                    <td className="py-3 font-medium">12 mins</td>
                    <td className="py-3 text-slate-400 text-xs">16:00 - 17:30</td>
                    <td className="py-3 text-right"><TrendingDown size={16} className="text-emerald-400 inline" /></td>
                  </tr>
                </tbody>
              </table>
           </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
