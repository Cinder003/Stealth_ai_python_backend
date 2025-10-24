import { PrismaClient, User } from '@prisma/client';
import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import { ApiError } from '../utils/ApiError';
import { findUserByEmail } from './user.service';
import crypto from 'crypto';

const prisma = new PrismaClient();

export const createUserService = async (data: Omit<User, 'id' | 'createdAt' | 'updatedAt'>) => {
  const existingUser = await findUserByEmail(data.email);
  if (existingUser) {
    throw new ApiError(409, 'User with this email already exists');
  }
  const hashedPassword = await bcrypt.hash(data.password, 10);
  return prisma.user.create({
    data: {
      ...data,
      password: hashedPassword,
    },
  });
};

const generateAccessToken = (user: User) => {
  return jwt.sign({ id: user.id }, process.env.JWT_ACCESS_SECRET!, { expiresIn: '15m' });
};

const generateRefreshToken = (user: User, jti: string) => {
  return jwt.sign({ id: user.id, jti }, process.env.JWT_REFRESH_SECRET!, { expiresIn: '7d' });
};

export const createTokens = async (user: User) => {
    const jti = crypto.randomUUID();
    const accessToken = generateAccessToken(user);
    const refreshToken = generateRefreshToken(user, jti);

    await prisma.refreshToken.create({
        data: {
            id: jti,
            hashedToken: crypto.createHash('sha256').update(refreshToken).digest('hex'),
            userId: user.id,
        }
    });

    return { accessToken, refreshToken };
};
