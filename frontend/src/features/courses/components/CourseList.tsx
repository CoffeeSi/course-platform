import CourseCard from "./CourseCard";
import {coursesApi} from "@/features/courses/api/courses.api";
import { cookies } from "next/headers";

export default async function CourseList() {
  const token = (await cookies()).get("access_token")?.value;
  const response = await coursesApi.fetchCourses(undefined, token);
  const courses = response.results;

  return (
    <ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 w-full">
      {courses?.map((course) => (
        <li key={course.id}>
          <CourseCard {...course} />
        </li>
      ))}
    </ul>
  )
}
