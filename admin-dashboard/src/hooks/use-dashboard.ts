import { useMemo } from 'react';
import { activityFeed, assets, dashboardMetrics, jobs, logs, monitoringServices, templates, users, workflowSeries } from '@/services/mock-data';

export function useDashboardData() {
  return useMemo(
    () => ({
      dashboardMetrics,
      activityFeed,
      workflowSeries,
      monitoringServices,
      jobs,
      templates,
      users,
      assets,
      logs
    }),
    []
  );
}

