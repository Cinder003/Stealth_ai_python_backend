// backend/src/routes/auth.routes.ts
import { Router } from 'express';
import { register, login, refreshToken, logout } from '../controllers/auth.controller';
import { validateRequest } from '../middleware/validateRequest';
import { registerSchema, loginSchema } from '../utils/validationSchemas';

const router = Router();

router.post('/register', validateRequest({ body: registerSchema }), register);
router.post('/login', validateRequest({ body: loginSchema }), login);
router.post('/refresh-token', refreshToken);
router.post('/logout', logout);

export default router;
