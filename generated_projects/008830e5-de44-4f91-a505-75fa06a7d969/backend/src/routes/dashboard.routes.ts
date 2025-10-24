// backend/src/routes/dashboard.routes.ts
import { Router } from 'express';
import { getDashboardData } from '../controllers/dashboard.controller';
import { protect } from '../middleware/auth.middleware';

const router = Router();

router.get('/', protect, getDashboardData);

export default router;
