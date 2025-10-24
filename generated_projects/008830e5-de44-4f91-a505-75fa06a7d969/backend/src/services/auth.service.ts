// backend/src/services/auth.service.ts
import { PrismaClient } from '@prisma/client';
import bcrypt from 'bcrypt';
import { createAccessToken, createRefreshToken, verifyRefreshToken } from '../utils/jwt';
import { RegisterInput, LoginInput } from '../utils/validationSchemas';

const prisma = new PrismaClient();

export const registerUser = async (input: RegisterInput) => {
  const existingUser = await prisma.user.findUnique({ where: { email: input.email } });
  if (existingUser) {
    throw new Error('User with this email already exists');
  }

  const hashedPassword = await bcrypt.hash(input.password, 10);
  const user = await prisma.user.create({
    data: {
      email: input.email,
      password: hashedPassword,
      name: input.name,
    },
  });

  const { password, ...userWithoutPassword } = user;
  const accessToken = createAccessToken({ userId: user.id });
  const refreshToken = createRefreshToken({ userId: user.id });

  return { user: userWithoutPassword, accessToken, refreshToken };
};

export const loginUser = async (input: LoginInput) => {
  const user = await prisma.user.findUnique({ where: { email: input.email } });
  if (!user || !(await bcrypt.compare(input.password, user.password))) {
    throw new Error('Invalid email or password');
  }

  const { password, ...userWithoutPassword } = user;
  const accessToken = createAccessToken({ userId: user.id });
  const refreshToken = createRefreshToken({ userId: user.id });

  return { user: userWithoutPassword, accessToken, refreshToken };
};

export const refreshAccessToken = async (token: string) => {
  const decoded = verifyRefreshToken(token);
  const newAccessToken = createAccessToken({ userId: decoded.userId });
  return { newAccessToken };
};
