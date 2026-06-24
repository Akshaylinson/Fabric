import type { JobStatus, Role, ServiceName } from '@/types';

export const dashboardMetrics = {
  system: [
    { label: 'Total Users', value: '248' },
    { label: 'Total Templates', value: '1,284' },
    { label: 'Fabric Render Jobs', value: '9,482' },
    { label: 'Try-On Jobs', value: '4,120' },
    { label: 'Generated Images', value: '14,607' },
    { label: 'Active Jobs', value: '31' },
    { label: 'Failed Jobs', value: '9' },
    { label: 'Average Generation Time', value: '12.4s' }
  ],
  ai: [
    { label: 'Workflow 1 Success Rate', value: '98.4%' },
    { label: 'Workflow 2 Success Rate', value: '96.9%' },
    { label: 'Workflow 3 Success Rate', value: '95.7%' },
    { label: 'GPU Utilization', value: '71%' },
    { label: 'Queue Length', value: '14' },
    { label: 'Average Processing Time', value: '8.2s' }
  ],
  storage: [
    { label: 'Total Storage Used', value: '3.4 TB' },
    { label: 'Uploaded Images', value: '82,214' },
    { label: 'Generated Outputs', value: '54,338' }
  ]
};

export const activityFeed = [
  { message: 'Template created.', time: '2 minutes ago', level: 'success' },
  { message: 'Fabric render completed.', time: '5 minutes ago', level: 'info' },
  { message: 'Try-on completed.', time: '12 minutes ago', level: 'success' },
  { message: 'User login.', time: '15 minutes ago', level: 'info' },
  { message: 'Failed job.', time: '21 minutes ago', level: 'error' }
];

export const workflowSeries = [
  { day: 'Mon', workflow1: 98, workflow2: 96, workflow3: 95 },
  { day: 'Tue', workflow1: 97, workflow2: 95, workflow3: 94 },
  { day: 'Wed', workflow1: 99, workflow2: 97, workflow3: 96 },
  { day: 'Thu', workflow1: 98, workflow2: 96, workflow3: 95 },
  { day: 'Fri', workflow1: 98, workflow2: 97, workflow3: 95 },
  { day: 'Sat', workflow1: 97, workflow2: 96, workflow3: 94 },
  { day: 'Sun', workflow1: 98, workflow2: 96, workflow3: 95 }
];

export const monitoringServices: Array<{
  name: ServiceName;
  status: 'Healthy' | 'Warning' | 'Down';
  uptime: string;
  responseTime: string;
}> = [
  { name: 'Gateway', status: 'Healthy', uptime: '99.98%', responseTime: '24ms' },
  { name: 'Auth Service', status: 'Healthy', uptime: '99.95%', responseTime: '31ms' },
  { name: 'Business Service', status: 'Healthy', uptime: '99.97%', responseTime: '42ms' },
  { name: 'Orchestrator', status: 'Warning', uptime: '99.21%', responseTime: '118ms' },
  { name: 'Template Service', status: 'Healthy', uptime: '99.94%', responseTime: '87ms' },
  { name: 'Fabric Service', status: 'Healthy', uptime: '99.93%', responseTime: '91ms' },
  { name: 'Try-On Service', status: 'Down', uptime: '98.71%', responseTime: '—' },
  { name: 'PostgreSQL', status: 'Healthy', uptime: '99.99%', responseTime: '11ms' },
  { name: 'Redis', status: 'Healthy', uptime: '99.98%', responseTime: '7ms' },
  { name: 'MinIO', status: 'Healthy', uptime: '99.96%', responseTime: '14ms' }
];

export const jobs = [
  { id: 'job_001', workflow: 'Template Creation', status: 'Completed' as JobStatus, createdAt: '2026-06-24 09:02', duration: '11.2s', user: 'Asha' },
  { id: 'job_002', workflow: 'Fabric Render', status: 'Running' as JobStatus, createdAt: '2026-06-24 09:10', duration: '6.8s', user: 'Dev' },
  { id: 'job_003', workflow: 'Try-On', status: 'Failed' as JobStatus, createdAt: '2026-06-24 09:16', duration: '9.4s', user: 'QA' }
];

export const templates = [
  { id: 'tpl_001', name: 'Classic Shirt', type: 'Shirt', createdBy: 'Designer A', createdDate: '2026-06-20', status: 'Active' },
  { id: 'tpl_002', name: 'Modern Kurta', type: 'Kurta', createdBy: 'Designer B', createdDate: '2026-06-21', status: 'Draft' }
];

export const users = [
  { name: 'Asha Kumar', email: 'asha@fabric.ai', role: 'Super Admin' as Role, status: 'Active', lastLogin: '5 min ago' },
  { name: 'Dev Patel', email: 'dev@fabric.ai', role: 'Developer' as Role, status: 'Active', lastLogin: '22 min ago' },
  { name: 'Nina Roy', email: 'nina@fabric.ai', role: 'QA Engineer' as Role, status: 'Disabled', lastLogin: '2 days ago' }
];

export const assets = [
  { name: 'customer_014.jpg', category: 'Customer Images', size: '2.3 MB' },
  { name: 'fabric_linen_blue.png', category: 'Fabric Images', size: '1.7 MB' },
  { name: 'tpl_001_preview.png', category: 'Templates', size: '3.1 MB' },
  { name: 'render_job_991.png', category: 'Rendered Garments', size: '4.5 MB' },
  { name: 'tryon_778.png', category: 'Try-On Results', size: '5.2 MB' }
];

export const logs = [
  { timestamp: '09:21:03', service: 'Template Service', severity: 'Info', message: 'Template package created successfully.' },
  { timestamp: '09:18:44', service: 'Orchestrator', severity: 'Warning', message: 'Job retry scheduled after adapter timeout.' },
  { timestamp: '09:16:08', service: 'Try-On Service', severity: 'Error', message: 'Pose adapter returned invalid keypoints.' }
];

