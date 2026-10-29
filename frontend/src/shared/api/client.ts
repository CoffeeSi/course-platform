
interface CustomRequestInit extends RequestInit {
  params?: Record<string, string | number | boolean | undefined | null>;
  token?: string;
}

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name = 'ApiError';
  }
}

const getBaseUrl = () => {
  if (typeof window !== 'undefined') {
    return process.env.NEXT_PUBLIC_API_BASE_URL || '';
  }

  return process.env.LOCAL_API_URL || process.env.BACKEND_URL || 'http://127.0.0.1:8000';
};

async function customFetch<T>(endpoint: string, options: CustomRequestInit = {}): Promise<T> {
  const baseUrl = getBaseUrl();
  let url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;

  const { params, token, headers: customHeaders, ...fetchOptions } = options;
  if (params) {
    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value));
      }
    });

    const queryString = searchParams.toString();
    if (queryString) {
      url += (url.includes('?') ? '&' : '?') + queryString;
    }
  }

  const headers = new Headers(customHeaders);
  if (!headers.has('Content-Type') && !(fetchOptions.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  if (token) {
    if (typeof window === 'undefined') {
      headers.set('Cookie', `access_token=${token}`);
    }
  }

  const response = await fetch(url, {
    ...fetchOptions,
    headers,
    credentials: 'include',
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new ApiError(
      errorData.message || errorData.detail || `HTTP Error: ${response.status}`,
      response.status
    );
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

export const client = {
  get: <T>(endpoint: string, options?: CustomRequestInit) =>
    customFetch<T>(endpoint, { ...options, method: 'GET' }),

  post: <T>(endpoint: string, body?: any, options?: CustomRequestInit) => {
    const isFormData = body instanceof FormData;
    return customFetch<T>(endpoint, {
      ...options,
      method: 'POST',
      body: isFormData ? body : JSON.stringify(body)
    });
  },

  patch: <T>(endpoint: string, body?: any, options?: CustomRequestInit) => {
    const isFormData = body instanceof FormData;
    return customFetch<T>(endpoint, {
      ...options,
      method: 'PATCH',
      body: isFormData ? body : JSON.stringify(body)
    });
  },

  delete: <T>(endpoint: string, options?: CustomRequestInit) =>
    customFetch<T>(endpoint, { ...options, method: 'DELETE' }),
};

export default client;