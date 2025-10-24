// backend/src/controllers/dashboard.controller.ts
import { Request, Response, NextFunction } from 'express';
import * as dashboardService from '../services/dashboard.service';

export const getDashboardData = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const data = dashboardService.fetchDashboardData();
    res.status(200).json(data);
  } catch (error) {
    next(error);
  }
};
