import { Request, Response, NextFunction } from 'express';
import { fetchDashboardAnalytics } from '../services/dashboard.service';

export const getAnalyticsData = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const data = await fetchDashboardAnalytics();
    res.json(data);
  } catch (error) {
    next(error);
  }
};
