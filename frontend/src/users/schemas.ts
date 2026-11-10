import { z } from 'zod';

const usernameSchema = z.string().superRefine((value, context) => {
  if (!value.trim()) {
    context.addIssue({ code: 'custom', message: 'Username is required' });
    return;
  }
  if (value.length < 3 || value.length > 64) {
    context.addIssue({ code: 'custom', message: 'Username must be between 3 and 64 characters' });
  }
  if (!/^[A-Za-z0-9_.-]+$/.test(value)) {
    context.addIssue({
      code: 'custom',
      message: 'Username can only contain letters, numbers, underscores, periods, and hyphens',
    });
  }
});

const emailSchema = z.string().superRefine((value, context) => {
  if (!value.trim()) {
    context.addIssue({ code: 'custom', message: 'Email is required' });
    return;
  }
  if (value.length > 120) {
    context.addIssue({ code: 'custom', message: 'Email must be less than 120 characters' });
  }
  if (!/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(value)) {
    context.addIssue({ code: 'custom', message: 'Invalid email format' });
  }
});

const requiredPasswordSchema = z.string().superRefine((value, context) => {
  if (!value) {
    context.addIssue({ code: 'custom', message: 'This field is required.' });
  } else if (value.length < 8) {
    context.addIssue({ code: 'custom', message: 'Field must be at least 8 characters long.' });
  }
});

const optionalPasswordSchema = z.string().superRefine((value, context) => {
  if (value && value.length < 8) {
    context.addIssue({ code: 'custom', message: 'Field must be at least 8 characters long.' });
  }
});

const roleSchema = z.string().superRefine((value, context) => {
  if (!value) {
    context.addIssue({ code: 'custom', message: 'Role is required' });
  } else if (value !== 'user' && value !== 'admin') {
    context.addIssue({ code: 'custom', message: 'Role must be one of: user, admin' });
  }
});

export const userCreateSchema = z.object({
  username: usernameSchema,
  email: emailSchema,
  password: requiredPasswordSchema,
  role: roleSchema,
});

export const userEditSchema = z.object({
  username: usernameSchema,
  email: emailSchema,
  password: optionalPasswordSchema,
  role: roleSchema,
});

export type UserFormValues = z.infer<typeof userCreateSchema>;
