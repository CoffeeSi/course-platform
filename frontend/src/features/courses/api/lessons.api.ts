import { cache } from "react";
import client from "@/shared/api/client";
import { Lesson } from "../types/course.type";

export const lessonsApi = {
  fetchLesson: cache((lessonId: number, token?: string) => {
    return client.get<Lesson>(`/api/v1/courses/lessons/${lessonId}/`, {
      token,
    });
  }),
};
