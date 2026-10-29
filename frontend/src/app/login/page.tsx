import {redirect} from "next/navigation";
import getCurrentUser from "@/features/auth/utils/getCurrentUser";
import {LoginForm} from "@/app/login/LoginForm";

export default async function LoginPage() {
  const user = await getCurrentUser();

  if (user) {
    redirect("/profile");
  }

  return (
    <>
      <main className="mx-auto w-full max-w-md px-4 py-16">
        <h1 className="mb-6 text-3xl font-bold">Login</h1>
        <LoginForm />
      </main>
    </>
  );
}
