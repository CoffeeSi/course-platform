import { cookies } from "next/headers";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { paymentsApi } from "../api/payments.api";
import type { Payment } from "../types/payment.types";

const statusLabels: Record<string, string> = {
  pending: "Ожидает оплаты",
  processing: "Обрабатывается",
  succeeded: "Оплачен",
  failed: "Не оплачен",
  canceled: "Отменен",
  refunded: "Возвращен",
};

export async function PaymentsHistory() {
  const token = (await cookies()).get("access_token")?.value;

  if (!token) {
    return null;
  }

  let payments: Payment[] = [];

  try {
    const response = await paymentsApi.fetchPayments(token);
    payments = response.results;
  } catch {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Платежи</CardTitle>
          <CardDescription>Не удалось загрузить историю платежей.</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Платежи</CardTitle>
        <CardDescription>История оплат за курсы.</CardDescription>
      </CardHeader>
      <CardContent>
        {payments.length === 0 ? (
          <p className="text-sm text-muted-foreground">Платежей пока нет.</p>
        ) : (
          <ul className="space-y-3">
            {payments.map((payment) => (
              <li key={payment.id} className="rounded-2xl border bg-background p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <p className="font-medium">{payment.course_details.title}</p>
                    <p className="text-sm text-muted-foreground">
                      {Number(payment.amount).toFixed(2)} {payment.currency.toUpperCase()} · {payment.provider}
                    </p>
                  </div>
                  <span className="text-sm text-muted-foreground">
                    {statusLabels[payment.status] || payment.status}
                  </span>
                </div>
                <p className="mt-2 text-xs text-muted-foreground">Создан: {new Date(payment.created_at).toLocaleString("ru-RU")}</p>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}