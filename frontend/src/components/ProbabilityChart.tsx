import React from 'react';

interface Props {
  probabilities: Record<string, number>;
}

const ProbabilityChart: React.FC<Props> = ({ probabilities }) => {
  const getColor = (label: string) => {
    switch (label) {
      case 'CN':
      case 'Healthy Control':
        return 'bg-emerald-600';
      case 'MCI':
        return 'bg-amber-500';
      case 'AD':
      case "Parkinson's Disease":
        return 'bg-rose-600';
      default:
        return 'bg-blue-600';
    }
  };

  const data = Object.entries(probabilities || {}).map(([label, val]) => ({
    label,
    value: (val || 0) * 100,
    color: getColor(label),
  }));

  return (
    <div className="space-y-3.5">
      {data.map(item => (
        <div key={item.label} className="flex items-center text-xs sm:text-sm">
          <div className="w-32 sm:w-40 font-bold text-slate-800 truncate pr-2">{item.label}</div>
          <div className="flex-1 h-3.5 bg-slate-100 rounded-full overflow-hidden mx-3 border border-slate-200 p-0.5">
            <div 
              className={`h-full ${item.color} rounded-full transition-all duration-500 shadow-xs`} 
              style={{ width: `${Math.max(item.value, 1)}%` }}
            />
          </div>
          <div className="w-16 text-right text-slate-800 font-mono text-xs font-extrabold bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
            {item.value.toFixed(1)}%
          </div>
        </div>
      ))}
    </div>
  );
};

export default ProbabilityChart;

