import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { revalidatePath } from "next/cache";
import { Button } from "@/components/ui/button";
import { enrollmentsApi } from "@/features/enrollments/api/enrollmets.api";
import { paymentsApi } from "@/features/payments/api/payments.api";

export async function EnrollButton({
  courseId,
  price,
  isAuthorized,
}: {
  courseId: number;
  price: string | number;
  isAuthorized?: boolean;
}) {
  const isFree = Number(price) === 0;
  const label = isFree ? "Записаться" : "Купить";

  if (!isAuthorized) {
    async function goToLogin() {
      "use server";
      redirect("/login");
    }

    return (
      <form action={goToLogin} className="flex items-center gap-4">
        <span className="text-2xl font-bold">{Number(price).toFixed(2)} ₸</span>
        <Button type="submit">{label}</Button>
      </form>
    );
  }

  const token = (await cookies()).get("access_token")?.value;

  let status;
  try {
    status = await enrollmentsApi.fetchEnrollmentStatus(courseId, token);
  } catch {
    return (
      <p className="text-sm text-destructive">Не удалось загрузить статус записи</p>
    );
  }

  if (status?.is_enrolled) return null;

  async function enroll() {
    "use server";
    const token = (await cookies()).get("access_token")?.value;

    if (isFree) {
      try {
        await enrollmentsApi.enrollToCourse(courseId, token);
      } catch {
        redirect(`/courses/${courseId}?payment_error=checkout_unavailable`);
      }
      revalidatePath(`/courses/${courseId}`);
      return;
    }

    let paymentUrl: string | undefined;
    try {
      const result = await paymentsApi.createCoursePayment(courseId, token);
      paymentUrl = result.paymentUrl || "";
    } catch {
      redirect(`/courses/${courseId}?payment_error=checkout_unavailable`);
    }

    if (paymentUrl) {
      redirect(paymentUrl);
    }
    redirect(`/courses/${courseId}?payment_error=checkout_unavailable`);
  }

  return (
    <form action={enroll} className="flex items-center gap-4">
      <span className="text-2xl font-bold">{Number(price).toFixed(2)} ₸</span>
      <Button type="submit">{label}</Button>
    </form>
  );
}
