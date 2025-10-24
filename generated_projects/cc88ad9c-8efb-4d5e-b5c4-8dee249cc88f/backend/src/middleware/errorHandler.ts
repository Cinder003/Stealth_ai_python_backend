import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { ApiError } from '../utils/ApiError';
import logger from '../utils/logger';

export const errorHandler = (err: Error, req: Request, res: Response, next: NextFunction) => {
  if (err instanceof ApiError) {
    logger.warn(`ApiError: ${err.statusCode} - ${err.message}`);
    return res.status(err.statusCode).json({ message: err.message });
  }

  if (err instanceof ZodError) {
    logger.warn(`Validation Error: ${JSON.stringify(err.errors)}`);
    return res.status(400).json({
      message: 'Validation failed',
      errors: err.errors.map(e => ({ field: e.path.join('.'), message: e.message })),
    });
  }

  logger.error(`Internal Server Error: ${err.message}`, { stack: err.stack });
  return res.status(500).json({ message: 'Internal Server Error' });
};
