import PaymentStatusHandler from "@/features/payments/components/PaymentStatusHandler";

export default async function PaymentSuccessPage({
  searchParams,
}: {
  searchParams: Promise<{ session_id?: string }>;
}) {
  const { session_id } = await searchParams;

  return (
    <div className="flex flex-col items-center justify-center gap-4 py-20">
      <h1 className="text-2xl font-bold">Оплата прошла успешно</h1>
      <PaymentStatusHandler sessionId={session_id} />
    </div>
  );
}