import { redirect } from "next/navigation";
import getCurrentUser from "@/features/auth/utils/getCurrentUser";
import { VerifyEmailForm } from "@/features/auth/components/VerifyEmailForm";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Подтверждение электронной почты",
};

export default async function VerifyEmailPage({
  searchParams,
}: {
  searchParams: Promise<{ email?: string }>;
}) {
  const user = await getCurrentUser();

  if (!user) redirect("/login");
  if (user.is_email_verified) redirect("/profile");

  const { email } = await searchParams;

  return (
    <VerifyEmailForm initialEmail={email || user.email} />
  );
}
