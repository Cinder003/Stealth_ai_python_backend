typescript
import { Router } from 'express';
import authRoutes from './auth.routes';
import messageRoutes from './message.routes';

const router = Router();

router.use('/auth', authRoutes);
router.use('/messages', messageRoutes);

export default router;
