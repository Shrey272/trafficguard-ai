import React from 'react';

const StatCard = ({ title, value, subtext, subtextColor, icon: Icon, valueColor = 'text-white' }) => {
  return (
    <div className="bg-dark-panel border border-dark-border rounded-lg p-5 flex flex-col justify-between">
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-slate-400 font-medium text-sm">{title}</h3>
        {Icon && <div className="text-slate-500"><Icon size={18} /></div>}
      </div>
      <div>
        <div className={`text-3xl font-bold mb-1 ${valueColor}`}>{value}</div>
        <div className={`text-xs ${subtextColor || 'text-slate-500'}`}>{subtext}</div>
      </div>
    </div>
  );
};

export default StatCard;
