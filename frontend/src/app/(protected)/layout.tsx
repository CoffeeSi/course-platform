import EmailVerificationGuard from "@/features/auth/components/EmailVerificationGuard";
import React from "react";

export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  return (
    <EmailVerificationGuard>
      {children}
    </EmailVerificationGuard>
  );
}