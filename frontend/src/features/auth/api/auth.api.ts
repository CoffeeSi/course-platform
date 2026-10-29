import client from '@/shared/api/client';
import type { LoginPayload, RegisterPayload } from '../types/auth.types';

export const authApi = {
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
