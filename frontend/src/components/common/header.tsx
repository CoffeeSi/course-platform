import Link from "next/link";
import getCurrentUser from "@/features/auth/utils/getCurrentUser";
import {LogoutButton} from "@/features/auth/components/LogoutButton";

export default async function Header() {

  const user = await getCurrentUser();

  return (
    <header className="w-full border-b">
      <div className="max-w-7xl mx-auto py-4 px-4 flex items-center justify-between gap-4">
        <Link href="/" className="text-2xl font-bold">Course Platform</Link>
        <nav className="flex items-center gap-4 text-sm font-medium">
          {(!user || user.is_email_verified) && (
            <Link href="/courses" className="hover:text-primary transition-colors">Курсы</Link>
          )}
          {user ? (
            <>
              {user.is_email_verified ? (
                <>
                  <Link href="/my-courses" className="hover:text-primary transition-colors">Мои курсы</Link>
                  <Link href="/profile" className="hover:text-primary transition-colors">{user.email}</Link>
                </>
              ) : (
                <span className="text-destructive bg-destructive/10 px-2 py-1 rounded text-xs">
                  {user.email} (Не подтвержден)
                </span>
              )}
              <LogoutButton />
            </>
          ) : (
            <>
              <Link href="/login" className="hover:text-primary transition-colors">Войти</Link>
              <Link href="/register" className="hover:text-primary transition-colors">Регистрация</Link>
            </>
          )}
        </nav>
      </div>
    </header>
  )
}
