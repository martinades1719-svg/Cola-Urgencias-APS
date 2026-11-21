import { queryOptions } from '@tanstack/react-query';
import { alertService, auditService, episodeService, queueService, reportService, userService } from '.';
export const dashboardQuery = () => queryOptions({queryKey:['dashboard'],queryFn:reportService.dashboard,refetchInterval:15000});
export const queueQuery = () => queryOptions({queryKey:['queue'],queryFn:queueService.list,refetchInterval:15000});
export const episodesQuery = () => queryOptions({queryKey:['episodes'],queryFn:episodeService.list,refetchInterval:15000});
export const pendingQuery = () => queryOptions({queryKey:['pending'],queryFn:episodeService.pending,refetchInterval:15000});
export const alertsQuery = () => queryOptions({queryKey:['alerts'],queryFn:alertService.list,refetchInterval:15000});
export const auditQuery = () => queryOptions({queryKey:['audit'],queryFn:auditService.list});
export const usersQuery = () => queryOptions({queryKey:['users'],queryFn:userService.list});
