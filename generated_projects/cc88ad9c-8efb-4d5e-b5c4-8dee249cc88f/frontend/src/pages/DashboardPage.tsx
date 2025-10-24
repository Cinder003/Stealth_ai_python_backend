import { useQuery } from '../hooks/useQuery';
import { DashboardAnalyticsData } from '../../../shared/types/dashboard';
import Spinner from '../components/common/Spinner';
import MetricCard from '../components/dashboard/MetricCard';
import SalesChart from '../components/dashboard/SalesChart';
import SourcePieChart from '../components/dashboard/SourcePieChart';

const DashboardPage = () => {
  const { data, isLoading, error } = useQuery<DashboardAnalyticsData>('/dashboard/analytics');

  if (isLoading) {
    return <div className="flex h-full items-center justify-center"><Spinner /></div>;
  }

  if (error) {
    return <div className="text-red-500 text-center p-4">Error: {error}</div>;
  }

  return (
    <div className="space-y-8 p-4 md:p-8">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {data?.kpis.map((kpi, index) => <MetricCard key={index} {...kpi} />)}
      </div>

      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4 rounded-xl bg-white p-4 shadow-sm dark:bg-gray-800">
          <h2 className="text-xl font-semibold mb-4">Overview</h2>
          {data && <SalesChart data={data.salesOverTime} />}
        </div>
        <div className="col-span-3 rounded-xl bg-white p-4 shadow-sm dark:bg-gray-800">
           <h2 className="text-xl font-semibold mb-4">Traffic Source</h2>
           {data && <SourcePieChart data={data.sources} />}
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
