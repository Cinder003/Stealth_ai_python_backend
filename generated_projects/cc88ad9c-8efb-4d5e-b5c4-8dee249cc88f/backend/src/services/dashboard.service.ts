import { DashboardAnalyticsData } from '../../../shared/types/dashboard';

// This is a mock service. In a real application, you would query your database.
export const fetchDashboardAnalytics = async (): Promise<DashboardAnalyticsData> => {
  return {
    kpis: [
      { title: 'Total Revenue', metric: '$45,231.89', change: '+20.1% from last month', changeType: 'increase' },
      { title: 'Subscriptions', metric: '+2350', change: '+180.1% from last month', changeType: 'increase' },
      { title: 'Sales', metric: '+12,234', change: '+19% from last month', changeType: 'increase' },
      { title: 'Active Now', metric: '+573', change: '+201 since last hour', changeType: 'increase' },
    ],
    salesOverTime: [
      { name: 'Jan', sales: 4000 },
      { name: 'Feb', sales: 3000 },
      { name: 'Mar', sales: 5000 },
      { name: 'Apr', sales: 4500 },
      { name: 'May', sales: 6000 },
      { name: 'Jun', sales: 5500 },
      { name: 'Jul', sales: 7000 },
    ],
    sources: [
        { name: 'Direct', value: 400 },
        { name: 'Referral', value: 300 },
        { name: 'Social', value: 200 },
        { name: 'Organic', value: 278 },
    ],
    recentActivities: [
      { id: '1', user: { name: 'Olivia Martin', avatar: '/avatars/01.png' }, action: 'purchased a new subscription.', timestamp: '5m ago' },
      { id: '2', user: { name: 'Jackson Lee', avatar: '/avatars/02.png' }, action: 'upgraded to the Pro plan.', timestamp: '15m ago' },
      { id: '3', user: { name: 'Isabella Nguyen', avatar: '/avatars/03.png' }, action: 'viewed the pricing page.', timestamp: '30m ago' },
      { id: '4', user: { name: 'William Kim', avatar: '/avatars/04.png' }, action: 'signed up for the newsletter.', timestamp: '1h ago' },
    ],
  };
};
