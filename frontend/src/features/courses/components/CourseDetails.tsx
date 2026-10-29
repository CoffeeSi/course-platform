import { Suspense } from "react";
import { coursesApi } from "@/features/courses/api/courses.api";
import { EnrollButton } from "./EnrollButton";
import getCurrentUser from "@/features/auth/utils/getCurrentUser";
import { cookies } from "next/headers";
import Link from "next/link";

export default async function CourseDetails({ courseID, paymentError }: { courseID: number; paymentError?: string }) {
  const token = (await cookies()).get("access_token")?.value;
  const user = await getCurrentUser();
  let course;

  try {
    course = await coursesApi.fetchCourse(courseID, token);
  } catch {
    return <p className="text-destructive">Курс не найден</p>;
  }

  if (!course) {
    return <p className="text-destructive">Курс не найден</p>;
  }

  return (
    <>
      <section className="flex flex-col gap-4">
        {paymentError ? (
          <p className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            Не удалось открыть checkout для оплаты. Платеж создан, но backend не вернул ссылку на оплату.
          </p>
        ) : null}
        <p className="text-sm text-muted-foreground">{course.category?.name}</p>
        <h1 className="text-4xl font-extrabold tracking-tight">{course.title}</h1>
        <p className="max-w-3xl text-muted-foreground">{course.description}</p>
        <Suspense fallback={<p className="text-sm text-muted-foreground">Загрузка...</p>}>
          <EnrollButton courseId={course.id} price={course.price} isAuthorized={user !== null} />
        </Suspense>
      </section>

      <section className="flex flex-col gap-4">
        <h2 className="text-2xl font-semibold">Модули</h2>
        {course.modules.length === 0 ? <p>No modules yet.</p> : null}
        <ul className="flex flex-col gap-4">
          {course.modules.map((module) => (
            <li key={module.id} className="rounded-md border p-4">
              <h3 className="font-semibold">{module.order}. {module.title}</h3>
              <ul className="mt-3 flex flex-col gap-2 text-sm">
                {(module.lessons ?? []).map((lesson) => (
                  <li key={lesson.id} className="rounded-md bg-muted px-3 py-2">
                    <Link href={`/lessons/${lesson.id}`}>{lesson.title}</Link>
                  </li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
