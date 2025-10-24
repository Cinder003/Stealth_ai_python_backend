export interface KpiData {
  title: string;
  metric: string;
  change: string;
  changeType: 'increase' | 'decrease';
}

export interface SalesOverTimeData {
  name: string;
  sales: number;
}

export interface SourceData {
  name: string;
  value: number;
}

export interface RecentActivity {
  id: string;
  user: {
    name: string;
    avatar: string;
  };
  action: string;
  timestamp: string;
}

export interface DashboardAnalyticsData {
  kpis: KpiData[];
  salesOverTime: SalesOverTimeData[];
  sources: SourceData[];
  recentActivities: RecentActivity[];
}
