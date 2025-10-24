import { PrismaClient } from '@prisma/client';
import jwt from 'jsonwebtoken';
import { ApiError } from '../utils/ApiError';
import { findUserById } from './user.service';
import { createTokens } from './auth.service';
import crypto from 'crypto';

const prisma = new PrismaClient();

export const verifyRefreshToken = async (token: string) => {
    try {
        const payload = jwt.verify(token, process.env.JWT_REFRESH_SECRET!) as { id: string, jti: string };
        const savedToken = await prisma.refreshToken.findUnique({
            where: { id: payload.jti }
        });

        if (!savedToken || savedToken.revoked) {
            throw new ApiError(401, 'Unauthorized');
        }

        const hashedToken = crypto.createHash('sha256').update(token).digest('hex');
        if (hashedToken !== savedToken.hashedToken) {
            throw new ApiError(401, 'Unauthorized');
        }

        const user = await findUserById(payload.id);
        if (!user) {
            throw new ApiError(401, 'Unauthorized');
        }

        // Revoke old token and generate new ones
        await prisma.refreshToken.update({
            where: { id: payload.jti },
            data: { revoked: true }
        });

        const { accessToken, refreshToken } = await createTokens(user);

        return { 
            accessToken, 
            refreshToken, 
            user: { id: user.id, email: user.email, name: user.name }
        };

    } catch (error) {
        throw new ApiError(401, 'Invalid refresh token');
    }
};
