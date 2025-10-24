// shared/types/index.ts

// User related types
export interface User {
  id: string;
  email: string;
  name: string | null;
  createdAt: Date;
  updatedAt: Date;
}

// API Response types
export interface AuthResponse {
  user: User;
  accessToken: string;
}

export interface ErrorResponse {
  message: string;
  errors?: { field: string; message: string }[];
}

// Dashboard data types
export interface StatCardData {
  title: string;
  value: string;
  change: number;
  changeType: 'increase' | 'decrease';
}

export interface SalesDataPoint {
  name: string;
  uv: number;
  pv: number;
  amt: number;
}

export interface RecentOrder {
  id: string;
  customerName: string;
  product: string;
  amount: number;
  status: 'pending' | 'shipped' | 'delivered' | 'cancelled';
}

export interface DashboardData {
  stats: StatCardData[];
  salesOverTime: SalesDataPoint[];
  recentOrders: RecentOrder[];
}
