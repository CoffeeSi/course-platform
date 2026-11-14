import { cache } from "react";
import client from "@/shared/api/client";
import { Enrollment, EnrollmentCreate, EnrollmentStatus, Progress } from "../types/enrollment.type";
import { PaginatedResponse } from "@/shared/types/types";

export const enrollmentsApi = {
    fetchEnrollments: (token?: string) => {
        return client.get<PaginatedResponse<Enrollment>>("/api/v1/enrollments/enrollments/", {
            token,
        });
    },
    fetchEnrollmentStatus: cache((courseId: number, token?: string) => {
        return client.get<EnrollmentStatus>(`/api/v1/enrollments/enrollments/${courseId}/status/`, {
            token,
        });
    }),
    enrollToCourse: (courseId: number, token?: string) => {
        return client.post<EnrollmentCreate>(
            "/api/v1/enrollments/enrollments/",
            { course: courseId },
            { token }
        );
    },
    fetchProgress: (token?: string) => {
        return client.get<Progress[]>("/api/v1/enrollments/progress/", {
            token,
        });
    },
    markProgressComplete: (id: number, token?: string) => {
        return client.post<Progress>(
            `/api/v1/enrollments/progress/${id}/mark_complete/`,
            {
                token,
            }
        );
    },
    markProgressIncomplete: (id: number, token?: string) => {
        return client.post<Progress>(
            `/api/v1/enrollments/progress/${id}/mark_incomplete/`,
            { token }
        );
    }
};