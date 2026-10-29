import client from "@/shared/api/client";
import { Lesson } from "../types/course.type";

export const lessonsApi = {
  fetchLesson: (lessonId: number, token?: string) => {
    return client.get<Lesson>(`/api/v1/courses/lessons/${lessonId}/`, {
      token,
      next: { revalidate: 0 },
    });
  }
};