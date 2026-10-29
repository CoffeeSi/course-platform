import { cache } from 'react';
import { cookies } from 'next/headers';
import { usersApi } from '@/features/users/api/users.api';

const getCurrentUser = cache(async () => {
  const cookieStore = await cookies();
  const token = cookieStore.get('access_token')?.value;

  if (!token) {
    return null;
  }

  try {
    return await usersApi.fetchProfile(token);
  } catch (error) {
    return null;
  }
});

export default getCurrentUser;