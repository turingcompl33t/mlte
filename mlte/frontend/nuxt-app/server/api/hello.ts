import { defineEventHandler } from 'h3';

export default defineEventHandler(() => {
  return { message: 'Hello World' };
});
