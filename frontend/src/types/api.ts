export interface ErrorDetail {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T | null;
  error: ErrorDetail | null;
  request_id?: string | null;
}

export class ApiRequestError extends Error {
  code: string;
  details?: Record<string, unknown>;

  constructor(error: ErrorDetail) {
    super(error.message);
    this.name = "ApiRequestError";
    this.code = error.code;
    this.details = error.details;
  }
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}
