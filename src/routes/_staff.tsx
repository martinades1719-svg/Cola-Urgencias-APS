import { createFileRoute } from '@tanstack/react-router';
import { StaffLayout } from '@/layouts/StaffLayout';
export const Route = createFileRoute('/_staff')({ component: StaffLayout });
