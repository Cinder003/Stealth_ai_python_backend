import { PublicUser } from './user';

export interface AuthResponse {
  user: PublicUser;
  accessToken: string;
  refreshToken: string;
}
