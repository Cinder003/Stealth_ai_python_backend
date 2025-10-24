// backend/src/services/dashboard.service.ts
// Define types locally since shared types are not accessible
interface StatItem {
  title: string;
  value: string;
  change: number;
  changeType: 'increase' | 'decrease';
}

interface SalesData {
  name: string;
  uv: number;
  pv: number;
  amt: number;
}

interface Order {
  id: string;
  customerName: string;
  product: string;
  amount: number;
  status: 'delivered' | 'shipped' | 'pending' | 'cancelled';
}

interface DashboardData {
  stats: StatItem[];
  salesOverTime: SalesData[];
  recentOrders: Order[];
}

// In a real application, this data would be fetched and aggregated from the database.
// For this example, we'll use mock data.
export const fetchDashboardData = (): DashboardData => {
  return {
    stats: [
      { title: 'Total Revenue', value: '$45,231.89', change: 20.1, changeType: 'increase' },
      { title: 'Subscriptions', value: '+2350', change: 180.1, changeType: 'increase' },
      { title: 'Sales', value: '+12,234', change: 19, changeType: 'increase' },
      { title: 'Active Now', value: '+573', change: 201, changeType: 'increase' },
    ],
    salesOverTime: [
      { name: 'Jan', uv: 4000, pv: 2400, amt: 2400 },
      { name: 'Feb', uv: 3000, pv: 1398, amt: 2210 },
      { name: 'Mar', uv: 2000, pv: 9800, amt: 2290 },
      { name: 'Apr', uv: 2780, pv: 3908, amt: 2000 },
      { name: 'May', uv: 1890, pv: 4800, amt: 2181 },
      { name: 'Jun', uv: 2390, pv: 3800, amt: 2500 },
      { name: 'Jul', uv: 3490, pv: 4300, amt: 2100 },
    ],
    recentOrders: [
      { id: 'ORD001', customerName: 'John Doe', product: 'Laptop', amount: 1200, status: 'delivered' },
      { id: 'ORD002', customerName: 'Jane Smith', product: 'Mouse', amount: 25, status: 'shipped' },
      { id: 'ORD003', customerName: 'Sam Green', product: 'Keyboard', amount: 75, status: 'pending' },
      { id: 'ORD004', customerName: 'Chris Lee', product: 'Monitor', amount: 300, status: 'cancelled' },
      { id: 'ORD005', customerName: 'Pat Kim', product: 'Webcam', amount: 50, status: 'delivered' },
    ],
  };
};
