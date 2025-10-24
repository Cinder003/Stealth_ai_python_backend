import { KpiData } from '../../../../shared/types/dashboard';

const MetricCard = ({ title, metric, change, changeType }: KpiData) => {
  const changeColor = changeType === 'increase' ? 'text-green-500' : 'text-red-500';

  return (
    <div className="rounded-xl border bg-white p-6 shadow-sm dark:bg-gray-800">
      <div className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</div>
      <div className="mt-1 text-3xl font-semibold">{metric}</div>
      <p className={`mt-1 text-xs ${changeColor}`}>{change}</p>
    </div>
  );
};

export default MetricCard;
