import { Request, Response, NextFunction } from 'express';
import { createTokens, createUserService } from '../services/auth.service';
import { findUserByEmail } from '../services/user.service';
import { ApiError } from '../utils/ApiError';
import bcrypt from 'bcrypt';
import { verifyRefreshToken } from '../services/token.service';

export const register = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password, name } = req.body;
    const user = await createUserService({ email, password, name });
    res.status(201).json({ message: 'User registered successfully', userId: user.id });
  } catch (error) {
    next(error);
  }
};

export const login = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { email, password } = req.body;
    const user = await findUserByEmail(email);

    if (!user || !(await bcrypt.compare(password, user.password))) {
      throw new ApiError(401, 'Invalid credentials');
    }

    const { accessToken, refreshToken } = await createTokens(user);

    res.cookie('refreshToken', refreshToken, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'strict',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
    });

    res.json({
      user: { id: user.id, email: user.email, name: user.name },
      accessToken,
    });
  } catch (error) {
    next(error);
  }
};

export const refreshToken = async (req: Request, res: Response, next: NextFunction) => {
    const sentRefreshToken = req.cookies.refreshToken;
    if (!sentRefreshToken) {
        return next(new ApiError(401, 'No refresh token provided'));
    }

    try {
        const { accessToken, refreshToken: newRefreshToken, user } = await verifyRefreshToken(sentRefreshToken);

        res.cookie('refreshToken', newRefreshToken, {
            httpOnly: true,
            secure: process.env.NODE_ENV === 'production',
            sameSite: 'strict',
            maxAge: 7 * 24 * 60 * 60 * 1000,
        });

        res.json({
            user,
            accessToken,
        });
    } catch (error) {
        next(error);
    }
};

export const logout = (req: Request, res: Response) => {
  res.cookie('refreshToken', '', {
    httpOnly: true,
    expires: new Date(0),
  });
  res.status(200).json({ message: 'Logged out successfully' });
};
