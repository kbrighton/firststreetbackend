import { z } from 'zod';

const optionalCustomerId = z.string().optional().superRefine((value, context) => {
  if (!value || !value.trim()) return;
  if (value.length > 5) {
    context.addIssue({ code: 'custom', message: 'Customer ID must be 5 characters or less' });
  }
  if (!/^[A-Za-z0-9]*$/.test(value)) {
    context.addIssue({ code: 'custom', message: 'Customer ID must contain only letters and numbers' });
  }
});

const optionalTitle = z.string().optional().superRefine((value, context) => {
  if (value && value.length > 100) {
    context.addIssue({ code: 'custom', message: 'Title must be less than 100 characters' });
  }
});

export const searchSchema = z.object({
  cust: optionalCustomerId,
  title: optionalTitle,
}).superRefine(({ cust, title }, context) => {
  if (!cust && !title) {
    context.addIssue({
      code: 'custom',
      path: ['cust'],
      message: 'At least one search field is required',
    });
  }
});

export type SearchFormValues = z.infer<typeof searchSchema>;

export const logSearchSchema = z.object({
  log: z.string().optional().superRefine((value, context) => {
    if (!value || !value.trim()) {
      context.addIssue({ code: 'custom', message: 'LOG # is required' });
      return;
    }
    if (value.length !== 5) {
      context.addIssue({ code: 'custom', message: 'LOG # must be exactly 5 characters' });
    }
    if (!/^[A-Za-z0-9]+$/.test(value)) {
      context.addIssue({ code: 'custom', message: 'LOG # must contain only letters and numbers' });
    }
  }),
});

export type LogSearchValues = z.infer<typeof logSearchSchema>;

function isValidDateValue(value: string): boolean {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split('-').map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year
    && date.getUTCMonth() === month - 1
    && date.getUTCDate() === day;
}

function requiredDate(fieldLabel: string) {
  return z.string().superRefine((value, context) => {
    if (!value) {
      context.addIssue({
        code: 'custom',
        message: `${fieldLabel} date is required`,
      });
    } else if (!isValidDateValue(value)) {
      context.addIssue({ code: 'custom', message: 'Not a valid date value.' });
    }
  });
}

export const dueoutSchema = z.object({
  start_date: requiredDate('Start'),
  end_date: requiredDate('End'),
}).superRefine(({ start_date, end_date }, context) => {
  if (
    isValidDateValue(start_date)
    && isValidDateValue(end_date)
    && end_date < start_date
  ) {
    context.addIssue({
      code: 'custom',
      path: ['end_date'],
      message: 'End date must be after start date',
    });
  }
});

export type DueoutFormValues = z.infer<typeof dueoutSchema>;

const ORDER_LOG_TYPES = ['TR', 'DP', 'AA', 'VG', 'DG', 'GM', 'DTF', 'PP'] as const;

function requiredOrderDate(message: string) {
  return z.string().superRefine((value, context) => {
    if (!value) {
      context.addIssue({ code: 'custom', message });
    } else if (!isValidDateValue(value)) {
      context.addIssue({ code: 'custom', message: 'Not a valid date value.' });
    }
  });
}

function optionalOrderDate() {
  return z.string().superRefine((value, context) => {
    if (value && !isValidDateValue(value)) {
      context.addIssue({ code: 'custom', message: 'Not a valid date value.' });
    }
  });
}

function optionalInteger(min: number, max: number | undefined, rangeMessage: string) {
  return z.string().superRefine((value, context) => {
    if (!value) return;
    if (!/^-?\d+$/.test(value)) {
      context.addIssue({ code: 'custom', message: 'Not a valid integer value.' });
      return;
    }
    const number = Number(value);
    if (number < min || (max !== undefined && number > max)) {
      context.addIssue({ code: 'custom', message: rangeMessage });
    }
  });
}

export const orderFormSchema = z.object({
  log: z.string().superRefine((value, context) => {
    if (!value.trim()) {
      context.addIssue({ code: 'custom', message: 'LOG# is required' });
      return;
    }
    if (value.length !== 5) {
      context.addIssue({ code: 'custom', message: 'LOG# must be exactly 5 characters' });
    }
    if (!/^[A-Za-z0-9]+$/.test(value)) {
      context.addIssue({ code: 'custom', message: 'LOG# must contain only letters and numbers' });
    }
  }),
  cust: z.string().superRefine((value, context) => {
    if (!value.trim()) {
      context.addIssue({ code: 'custom', message: 'Customer# is required' });
      return;
    }
    if (value.length !== 5) {
      context.addIssue({ code: 'custom', message: 'Customer# must be exactly 5 characters' });
    }
    if (!/^[A-Za-z0-9]+$/.test(value)) {
      context.addIssue({ code: 'custom', message: 'Customer# must contain only letters and numbers' });
    }
  }),
  title: z.string().superRefine((value, context) => {
    if (!value.trim()) {
      context.addIssue({ code: 'custom', message: 'Title is required' });
    } else if (value.length > 100) {
      context.addIssue({ code: 'custom', message: 'Title must be less than 100 characters' });
    }
  }),
  datin: requiredOrderDate('Date In is required'),
  artout: optionalOrderDate(),
  dueout: optionalOrderDate(),
  print_n: optionalInteger(1, undefined, 'Quantity must be a positive number'),
  artlo: z.string().superRefine((value, context) => {
    if (!value) return;
    if (value.length > 20) {
      context.addIssue({ code: 'custom', message: 'Art Log must be less than 20 characters' });
    }
    if (!/^[A-Za-z0-9\-_]*$/.test(value)) {
      context.addIssue({
        code: 'custom',
        message: 'Art Log must contain only letters, numbers, hyphens, and underscores',
      });
    }
  }),
  rush: z.boolean(),
  prior: optionalInteger(1, 10, 'Priority must be between 1 and 10'),
  logtype: z.string().superRefine((value, context) => {
    if (!value) {
      context.addIssue({ code: 'custom', message: 'Log Type is required' });
    } else if (!ORDER_LOG_TYPES.includes(value as (typeof ORDER_LOG_TYPES)[number])) {
      context.addIssue({ code: 'custom', message: 'Not a valid choice.' });
    }
  }),
  colorf: optionalInteger(0, undefined, 'Number of colors must be a non-negative number'),
  ref_artlo: z.string().superRefine((value, context) => {
    if (!value) return;
    if (value.length !== 5) {
      context.addIssue({ code: 'custom', message: 'Art Reference must be exactly 5 characters' });
    }
    if (!/^[A-Za-z0-9]*$/.test(value)) {
      context.addIssue({ code: 'custom', message: 'Art Reference must contain only letters and numbers' });
    }
  }),
  howship: optionalInteger(1, undefined, 'How Shipped must be a positive number'),
  artno: z.string().superRefine((value, context) => {
    if (!value) return;
    if (value.length < 4 || value.length > 5) {
      context.addIssue({ code: 'custom', message: 'Artist ID must be between 4 and 5 characters' });
    }
    if (!/^[A-Za-z0-9]*$/.test(value)) {
      context.addIssue({ code: 'custom', message: 'Artist ID must contain only letters and numbers' });
    }
  }),
  datout: optionalOrderDate(),
});

export type OrderFormValues = z.infer<typeof orderFormSchema>;