// frontend/src/components/dashboard/StatCard.tsx
import { StatCardData } from '../../../../shared/types';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

const StatCard = ({ title, value, change, changeType }: StatCardData) => {
  const isIncrease = changeType === 'increase';
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-sm font-medium text-gray-500">{title}</h3>
      <div className="mt-2 flex items-baseline">
        <p className="text-2xl font-semibold">{value}</p>
        <span className={`ml-2 flex items-baseline text-sm font-semibold ${isIncrease ? 'text-green-600' : 'text-red-600'}`}>
          {isIncrease ? <ArrowUpRight className="h-4 w-4" /> : <ArrowDownRight className="h-4 w-4" />}
          {change}%
        </span>
      </div>
    </div>
  );
};

export default StatCard;
