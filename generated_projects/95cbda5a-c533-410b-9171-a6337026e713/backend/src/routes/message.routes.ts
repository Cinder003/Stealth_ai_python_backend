typescript
import { Router } from 'express';
import { getPublicMessage, getProtectedMessage } from '../controllers/message.controller';
import { authMiddleware } from '../middleware/authMiddleware';

const router = Router();

/**
 * @openapi
 * /api/messages/public:
 *   get:
 *     tags:
 *       - Messages
 *     summary: Get a public message
 *     responses:
 *       200:
 *         description: Success
 */
router.get('/public', getPublicMessage);

/**
 * @openapi
 * /api/messages/protected:
 *   get:
 *     tags:
 *       - Messages
 *     summary: Get a protected message
 *     security:
 *       - bearerAuth: []
 *     responses:
 *       200:
 *         description: Success
 *       401:
 *         description: Unauthorized
 */
router.get('/protected', authMiddleware, getProtectedMessage);

export default router;
