import React from 'react';
import { ArrowDown } from 'lucide-react';

interface Props {
  agentsExecuted: string[];
}

const AgentWorkflow: React.FC<Props> = ({ agentsExecuted }) => {
  return (
    <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200 mb-6">
      <h3 className="text-xs font-bold text-slate-500 mb-4 uppercase tracking-wider">Multi-Agent Workflow Execution Order</h3>
      <div className="flex flex-col items-center space-y-1">
        {agentsExecuted.map((agent, index) => (
          <React.Fragment key={agent}>
            <div className="bg-white px-5 py-2.5 rounded-xl border border-teal-200 shadow-xs text-sm font-bold text-teal-900 w-72 text-center">
              {agent}
            </div>
            {index < agentsExecuted.length - 1 && (
              <div className="py-1 text-slate-400">
                <ArrowDown size={18} />
              </div>
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};

export default AgentWorkflow;
