import { Button } from "@/components/ui/button";
import Link from "next/link";
import { Enrollment } from "@/features/enrollments/types/enrollment.type";
import { enrollmentsApi } from "@/features/enrollments/api/enrollmets.api";
import { cookies } from "next/headers";

export async function EnrollmentCard({ enrollment }: { enrollment: Enrollment }) {
    const token = (await cookies()).get("access_token")?.value;
    const status = await enrollmentsApi.fetchEnrollmentStatus(enrollment.id, token);

    return (
        <li className="rounded-md border p-4">
            <h2 className="text-xl font-semibold">{enrollment.course_details.title}</h2>
            <p className="mt-2 text-sm text-muted-foreground">
                {enrollment.course_details.description}
            </p>
            <p className="mt-3 text-sm">
                Выполнено: {status?.progress_percent ?? 0}%
            </p>
            <Button className="mt-4" variant="outline" asChild>
                <Link href={`/courses/${enrollment.course}`}>Перейти к курсу</Link>
            </Button>
        </li>
    )
}