typescript
import express, { Express, Request, Response } from 'express';
import dotenv from 'dotenv';
import cors from 'cors';
import helmet from 'helmet';
import cookieParser from 'cookie-parser';
import { rateLimit } from 'express-rate-limit';
import { errorHandler } from './middleware/errorHandler';
import logger from './utils/logger';
import apiRoutes from './routes';
import swaggerDocs from './utils/swagger';

dotenv.config();

const app: Express = express();
const PORT = process.env.PORT || 3000;

// Security Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN,
  credentials: true,
}));

// Rate Limiting
const limiter = rateLimit({
	windowMs: 15 * 60 * 1000, // 15 minutes
	limit: 100, // Limit each IP to 100 requests per `window` (here, per 15 minutes).
	standardHeaders: 'draft-7',
	legacyHeaders: false,
});
app.use(limiter);

// Parsers
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// API Routes
app.use('/api', apiRoutes);

// Swagger Docs
swaggerDocs(app, PORT as number);

// Health Check
app.get('/health', (req: Request, res: Response) => {
  res.status(200).send('OK');
});

// Error Handling Middleware
app.use(errorHandler);

app.listen(PORT, () => {
  logger.info(`Server is running at http://localhost:${PORT}`);
});

export default app;
