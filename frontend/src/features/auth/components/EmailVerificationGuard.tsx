import {redirect} from "next/navigation";
import getCurrentUser from "@/features/auth/utils/getCurrentUser";

export default async function EmailVerificationGuard({ children }: { children: React.ReactNode }) {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  if (!user.is_email_verified) {
    redirect("/register/verify-email");
  }

  return <>{children}</>;
}