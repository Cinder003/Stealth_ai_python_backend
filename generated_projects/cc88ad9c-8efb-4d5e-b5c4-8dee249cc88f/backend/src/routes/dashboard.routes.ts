import { Router } from 'express';
import { getAnalyticsData } from '../controllers/dashboard.controller';
import { protect } from '../middleware/authHandler';

const router = Router();

/**
 * @openapi
 * /api/dashboard/analytics:
 *   get:
 *     tags: [Dashboard]
 *     summary: Get dashboard analytics data
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Analytics data fetched successfully
 *       401:
 *         description: Unauthorized
 */
router.get('/analytics', protect, getAnalyticsData);

export default router;
