// backend/src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { logger } from '../utils/logger';

const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  logger.error(err);

  if (err instanceof ZodError) {
    return res.status(400).json({
      message: 'Validation failed',
      errors: err.errors.map(e => ({ field: e.path.join('.'), message: e.message })),
    });
  }

  // Add more specific error types here
  // e.g., if (err instanceof Prisma.PrismaClientKnownRequestError) { ... }

  return res.status(500).json({ message: 'An unexpected error occurred' });
};

export default errorHandler;
