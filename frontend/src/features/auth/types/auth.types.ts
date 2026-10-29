export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = {
  email: string;
  phone_number?: string | null;
  password: string;
  password_confirm: string;
};

export type MessageResponse = {
  message?: string;
  detail?: string;
};
