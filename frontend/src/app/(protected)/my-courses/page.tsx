import { cookies } from "next/headers";
import { EnrollmentCard } from "@/features/enrollments/components/EnrollmentCard";
import { enrollmentsApi } from "@/features/enrollments/api/enrollmets.api";
import { Enrollment } from "@/features/enrollments/types/enrollment.type";

export default async function MyCoursesPage() {
  const token = (await cookies()).get("access_token")?.value;

  let enrollments: Enrollment[];
  try {
    const response = await enrollmentsApi.fetchEnrollments(token);
    enrollments = response.results;
  } catch {
    return (
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-16">
        <h1 className="text-3xl font-bold">Мои курсы</h1>
        <p className="text-destructive">Не удалось загрузить приобретенные курсы</p>
      </main>
    );
  }

  return (
    <>
      <main className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-16">
        <h1 className="text-3xl font-bold">Мои курсы</h1>
        {enrollments.length === 0 ? <p>У вас ещё нет курсов</p> : null}
        <ul className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {enrollments.map((enrollment) => (
            <EnrollmentCard key={enrollment.id} enrollment={enrollment} />
          ))}
        </ul>
      </main>
    </>
  );
}
