typescript
// Generic API response structure
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface ApiErrorResponse {
  success: boolean;
  message: string;
  errors?: { field: string; message: string }[];
}

// Authentication
export interface AuthResponse {
  user: {
    id: string;
    email: string;
    name: string | null;
  };
  accessToken: string;
}

// Messages
export interface MessageResponse {
  message: string;
}
