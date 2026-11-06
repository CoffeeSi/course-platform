import { redirect } from "next/navigation";
import getCurrentUser from "@/features/auth/utils/getCurrentUser";
import { LoginForm } from "@/features/auth/components/LoginForm";
import GoogleLoginButton from "../../features/auth/components/GoogleLoginButton/GoogleLoginButton";

export default async function LoginPage() {
  const user = await getCurrentUser();

  if (user) {
    redirect("/profile");
  }

  return (
    <>
      <main className="mx-auto w-full max-w-md px-4 py-16">
        <h1 className="mb-6 text-3xl font-bold">Вход</h1>
        <div className="mb-4">
          <GoogleLoginButton />
        </div>
        <LoginForm />
      </main>
    </>
  );
}
