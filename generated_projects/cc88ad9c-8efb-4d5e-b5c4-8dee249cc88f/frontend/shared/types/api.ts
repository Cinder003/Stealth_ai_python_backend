export interface ApiErrorResponse {
  message: string;
  errors?: { field: string; message: string }[];
}
