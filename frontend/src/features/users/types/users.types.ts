export type Role = "student" | "instructor" | "admin";

export type Profile = {
    first_name?: string;
    last_name?: string;
    avatar?: string;
};

export type UserProfile = {
    id: number;
    email: string;
    phone_number: string | null;
    role: Role;
    is_email_verified: boolean;
    is_phone_verified: boolean;
    profile?: Profile;
    created_at: string;
    updated_at: string;
};