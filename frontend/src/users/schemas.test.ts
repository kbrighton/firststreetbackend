import { describe, expect, it } from 'vitest';
import { userCreateSchema, userEditSchema } from './schemas';

const validUser = {
  username: 'validname',
  email: 'valid@example.com',
  password: 'validpass123',
  role: 'user',
};

function firstMessage(result: ReturnType<typeof userCreateSchema.safeParse>) {
  return result.success ? undefined : result.error.issues[0]?.message;
}

describe('user form schemas', () => {
  it('matches username, email, password, and role validation messages', () => {
    expect(firstMessage(userCreateSchema.safeParse({ ...validUser, username: 'ab' })))
      .toBe('Username must be between 3 and 64 characters');
    expect(firstMessage(userCreateSchema.safeParse({ ...validUser, username: 'bad name' })))
      .toBe('Username can only contain letters, numbers, underscores, periods, and hyphens');
    expect(firstMessage(userCreateSchema.safeParse({ ...validUser, email: 'invalid' })))
      .toBe('Invalid email format');
    expect(firstMessage(userCreateSchema.safeParse({ ...validUser, email: 'x'.repeat(111) + '@example.com' })))
      .toBe('Email must be less than 120 characters');
    expect(firstMessage(userCreateSchema.safeParse({ ...validUser, password: '' })))
      .toBe('This field is required.');
    expect(firstMessage(userCreateSchema.safeParse({ ...validUser, password: 'short' })))
      .toBe('Field must be at least 8 characters long.');
    expect(firstMessage(userCreateSchema.safeParse({ ...validUser, role: 'owner' })))
      .toBe('Role must be one of: user, admin');
  });

  it('allows an unchanged password on edit but validates a supplied password', () => {
    expect(userEditSchema.safeParse({ ...validUser, password: '' }).success).toBe(true);
    expect(firstMessage(userEditSchema.safeParse({ ...validUser, password: 'short' })))
      .toBe('Field must be at least 8 characters long.');
  });
});
