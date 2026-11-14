import { cache } from 'react';
import client from '@/shared/api/client';
import type { UserProfile } from '../types/users.types';

export const usersApi = {
    fetchProfile: cache((token?: string) => {
        return client.get<UserProfile>('/api/v1/users/profile/', {
            token,
        });
    }),
    updateProfile: (payload: Partial<UserProfile>, token?: string) => {
        return client.patch<UserProfile>('/api/v1/users/profile/', payload, {
            token,
        });
    }
};