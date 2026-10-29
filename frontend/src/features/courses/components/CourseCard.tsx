import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import type { Course } from "../types/course.type";

export default function CourseCard(course: Course) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{course.title}</CardTitle>
      </CardHeader>
      <CardContent>
        <p>{course.description}</p>
        <div className="mt-4"></div>
        <div className="flex justify-between">
          <h1 className="text-2xl font-bold">{Number(course.price).toFixed(2)} ₸</h1>
          <Button variant="outline" asChild>
            <Link href={`/courses/${course.id}`}>Перейти к курсу</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
