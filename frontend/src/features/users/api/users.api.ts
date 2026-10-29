import client from '@/shared/api/client';
import type { UserProfile } from '../types/users.types';

export const usersApi = {
    fetchProfile: (token?: string) => {
        return client.get<UserProfile>('/api/v1/users/profile/', {
            token,
            next: { revalidate: 0 },
        });
    },
    updateProfile: (payload: Partial<UserProfile>, token?: string) => {
        return client.patch<UserProfile>('/api/v1/users/profile/', payload, {
            token,
        });
    }
};