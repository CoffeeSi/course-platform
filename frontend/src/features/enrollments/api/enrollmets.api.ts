import client from "@/shared/api/client";
import {Enrollment, EnrollmentCreate, EnrollmentStatus, Progress} from "../types/enrollment.type";
import { PaginatedResponse } from "@/shared/types/types";

export const enrollmentsApi = {
    fetchEnrollments: (token?: string) => {
        return client.get<PaginatedResponse<Enrollment>>("/api/v1/enrollments/enrollments/", {
            token,
            next: { revalidate: 0 },
        });
    },
    fetchEnrollmentStatus: (courseId: number, token?: string) => {
        return client.get<EnrollmentStatus>(`/api/v1/enrollments/enrollments/${courseId}/status/`, {
            token,
            next: { revalidate: 0 },
        });
    },
    enrollToCourse: (courseId: number, token?: string) => {
        return client.post<EnrollmentCreate>(
            "/api/v1/enrollments/enrollments/",
            { course: courseId },
            { token, next: { revalidate: 0 } }
        );
    },
    fetchProgress: (token?: string) => {
        return client.get<Progress[]>("/api/v1/enrollments/progress/", {
            token,
            next: { revalidate: 0 },
        });
    },
    markProgressComplete: (id: number, token?: string) => {
        return client.post<Progress>(
            `/api/v1/enrollments/progress/${id}/mark_complete/`,
            {
                token,
                next: { revalidate: 0 },
            });
    },
    markProgressIncomplete: (id: number, token?: string) => {
        return client.post<Progress>(`/api/v1/enrollments/progress/${id}/mark_incomplete/`, { token }, { next: { revalidate: 0 } });
    }
};