// backend/src/controllers/auth.controller.ts
import { Request, Response, NextFunction } from 'express';
import * as authService from '../services/auth.service';
import { verifyRefreshToken } from '../utils/jwt';

const SEVEN_DAYS_IN_MS = 7 * 24 * 60 * 60 * 1000;

export const register = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password, name } = req.body;
    const { user, accessToken, refreshToken } = await authService.registerUser({ email, password, name });

    res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: process.env.NODE_ENV === 'production', maxAge: SEVEN_DAYS_IN_MS });
    res.status(201).json({ user, accessToken });
  } catch (error) {
    next(error);
  }
};

export const login = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password } = req.body;
    const { user, accessToken, refreshToken } = await authService.loginUser({ email, password });

    res.cookie('refreshToken', refreshToken, { httpOnly: true, secure: process.env.NODE_ENV === 'production', maxAge: SEVEN_DAYS_IN_MS });
    res.status(200).json({ user, accessToken });
  } catch (error) {
    next(error);
  }
};

export const refreshToken = async (req: Request, res: Response, next: NextFunction) => {
  const token = req.cookies.refreshToken;
  if (!token) {
    return res.status(401).json({ message: 'No refresh token provided' });
  }

  try {
    const { newAccessToken } = await authService.refreshAccessToken(token);
    return res.json({ accessToken: newAccessToken });
  } catch (error) {
    next(error);
  }
};

export const logout = (req: Request, res: Response) => {
  res.cookie('refreshToken', '', { httpOnly: true, expires: new Date(0) });
  res.status(200).json({ message: 'Logged out successfully' });
};
