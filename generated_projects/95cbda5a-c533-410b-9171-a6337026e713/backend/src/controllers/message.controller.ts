typescript
import { Request, Response } from 'express';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export const getPublicMessage = (req: Request, res: Response) => {
  res.status(200).json({ success: true, data: { message: 'Hello, World!' } });
};

export const getProtectedMessage = async (req: Request, res: Response) => {
  // The user object is attached to the request by the authMiddleware
  const userId = (req as any).user.id;
  const user = await prisma.user.findUnique({ where: { id: userId } });

  res.status(200).json({
    success: true,
    data: { message: `Hello, ${user?.name || user?.email}! This is a protected message.` },
  });
};
