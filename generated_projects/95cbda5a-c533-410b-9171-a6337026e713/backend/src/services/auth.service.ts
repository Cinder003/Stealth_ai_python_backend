typescript
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { AppError } from '../utils/AppError';
import { RegisterInput, LoginInput } from '../utils/validationSchemas';

const prisma = new PrismaClient();

const generateTokens = (userId: string) => {
  const accessToken = jwt.sign({ id: userId }, process.env.ACCESS_TOKEN_SECRET!, {
    expiresIn: process.env.ACCESS_TOKEN_EXPIRATION,
  });
  const refreshToken = jwt.sign({ id: userId }, process.env.REFRESH_TOKEN_SECRET!, {
    expiresIn: process.env.REFRESH_TOKEN_EXPIRATION,
  });
  return { accessToken, refreshToken };
};

export const registerUser = async (data: RegisterInput) => {
  const existingUser = await prisma.user.findUnique({ where: { email: data.email } });
  if (existingUser) {
    throw new AppError('User with this email already exists', 409);
  }

  const hashedPassword = await bcrypt.hash(data.password, 10);
  const user = await prisma.user.create({
    data: {
      email: data.email,
      password: hashedPassword,
      name: data.name,
    },
  });

  const { accessToken, refreshToken } = generateTokens(user.id);
  const { password, ...userWithoutPassword } = user;

  return { user: userWithoutPassword, accessToken, refreshToken };
};

export const loginUser = async (data: LoginInput) => {
  const user = await prisma.user.findUnique({ where: { email: data.email } });
  if (!user) {
    throw new AppError('Invalid credentials', 401);
  }

  const isPasswordValid = await bcrypt.compare(data.password, user.password);
  if (!isPasswordValid) {
    throw new AppError('Invalid credentials', 401);
  }

  const { accessToken, refreshToken } = generateTokens(user.id);
  const { password, ...userWithoutPassword } = user;

  return { user: userWithoutPassword, accessToken, refreshToken };
};

export const refreshAccessToken = (token: string) => {
  if (!token) {
    throw new AppError('Refresh token not found', 401);
  }

  try {
    const decoded = jwt.verify(token, process.env.REFRESH_TOKEN_SECRET!) as { id: string };
    const { accessToken } = generateTokens(decoded.id);
    return { accessToken };
  } catch (error) {
    throw new AppError('Invalid refresh token', 403);
  }
};
