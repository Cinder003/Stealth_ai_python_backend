// frontend/src/pages/DashboardPage.tsx
import { useEffect, useState } from 'react';
import { DashboardData } from '../../../../shared/types';
import { getDashboardData } from '../services/dashboardService';
import StatCard from '../components/dashboard/StatCard';
import SalesChart from '../components/dashboard/SalesChart';
import RecentOrdersTable from '../components/dashboard/RecentOrdersTable';
import Spinner from '../components/ui/Spinner';

const DashboardPage = () => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const result = await getDashboardData();
        setData(result);
      } catch (err) {
        setError('Failed to fetch dashboard data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <div className="flex items-center justify-center h-full"><Spinner /></div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  if (!data) {
    return <div>No data available.</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {data.stats.map((stat, index) => (
          <StatCard key={index} {...stat} />
        ))}
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        <div className="col-span-4 p-4 bg-white rounded-lg shadow">
          <h2 className="mb-4 text-lg font-semibold">Sales Overview</h2>
          <SalesChart data={data.salesOverTime} />
        </div>
        <div className="col-span-3 p-4 bg-white rounded-lg shadow">
          <h2 className="mb-4 text-lg font-semibold">Recent Orders</h2>
          <RecentOrdersTable orders={data.recentOrders} />
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
