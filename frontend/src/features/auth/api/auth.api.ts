import client from '@/shared/api/client';
import type { LoginPayload, RegisterPayload } from '../types/auth.types';

export const authApi = {
    getCsrfToken: async (): Promise<string> => {
        // OAuth starts on this origin so the token matches the form's CSRF cookie.
        const response = await fetch('/api/v1/users/csrf/', {
            credentials: 'same-origin',
            cache: 'no-store',
        });

        if (!response.ok) {
            throw new Error('Не удалось подготовить вход');
        }

        const data: unknown = await response.json();

        if (
            !data || typeof data !== 'object' ||
            !('csrfToken' in data) ||
            typeof data.csrfToken !== 'string' || !data.csrfToken
        ) {
            throw new Error('Сервер не вернул CSRF-токен');
        }

        return data.csrfToken;
    },

    login: (credentials: LoginPayload) => {
        return client.post('/api/v1/users/login/', credentials);
    },

    register: (userData: RegisterPayload) => {
        return client.post('/api/v1/users/register/', userData);
    },

    logout: () => {
        return client.post('/api/v1/users/logout/', {});
    },

    refreshToken: () => {
        return client.post('/api/v1/users/token/refresh/', {});
    },

    verifyEmail: (verifyData: { email: string; code: string }) => {
        return client.post('/api/v1/users/verify-email/', verifyData);
    },

    resendEmailVerification: (email: string) => {
        return client.post('/api/v1/users/resend-email-verification/', { email });
    }
};
