'use client';

import { useRouter } from 'next/navigation';
import { authApi } from '@/features/auth/api/auth.api';

export function LogoutButton() {
  const router = useRouter();

  const handleLogout = async () => {
    await authApi.logout();

    router.push('/login');
    router.refresh();
  };

  return (
    <button
      onClick={handleLogout}
      className="text-sm font-medium hover:text-red-500 transition-colors cursor-pointer"
    >
      Выйти
    </button>
  );
}