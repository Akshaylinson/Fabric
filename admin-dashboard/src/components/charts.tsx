'use client';

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Bar,
  BarChart,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Card, SectionTitle } from '@/components/ui';
import { workflowSeries } from '@/services/mock-data';

const colors = ['#22d3ee', '#34d399', '#f59e0b'];

export function WorkflowChart() {
  return (
    <Card className="h-[360px]">
      <SectionTitle eyebrow="AI Metrics" title="Workflow Success Rates" description="Rolling weekly view across the three core AI workflows." />
      <div className="mt-4 h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={workflowSeries}>
            <defs>
              <linearGradient id="workflow1" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.45} />
                <stop offset="95%" stopColor="#22d3ee" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="workflow2" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#34d399" stopOpacity={0.45} />
                <stop offset="95%" stopColor="#34d399" stopOpacity={0.05} />
              </linearGradient>
              <linearGradient id="workflow3" x1="0" x2="0" y1="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.45} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
            <XAxis dataKey="day" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Area type="monotone" dataKey="workflow1" stroke="#22d3ee" fill="url(#workflow1)" />
            <Area type="monotone" dataKey="workflow2" stroke="#34d399" fill="url(#workflow2)" />
            <Area type="monotone" dataKey="workflow3" stroke="#f59e0b" fill="url(#workflow3)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export function StorageChart() {
  const data = [
    { name: 'Templates', value: 38 },
    { name: 'Generated', value: 44 },
    { name: 'Uploads', value: 18 }
  ];
  return (
    <Card className="h-[360px]">
      <SectionTitle eyebrow="Storage" title="Storage Distribution" description="Current object storage usage mix across major asset groups." />
      <div className="mt-4 h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip />
            <Pie data={data} dataKey="value" innerRadius={70} outerRadius={100} paddingAngle={4}>
              {data.map((entry, index) => (
                <Cell key={entry.name} fill={colors[index % colors.length]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

export function JobsChart() {
  const data = [
    { name: 'Mon', jobs: 124 },
    { name: 'Tue', jobs: 150 },
    { name: 'Wed', jobs: 143 },
    { name: 'Thu', jobs: 171 },
    { name: 'Fri', jobs: 181 },
    { name: 'Sat', jobs: 136 },
    { name: 'Sun', jobs: 119 }
  ];
  return (
    <Card className="h-[360px]">
      <SectionTitle eyebrow="Usage" title="Jobs per Day" description="Platform execution trend across the current week." />
      <div className="mt-4 h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
            <XAxis dataKey="name" stroke="#94a3b8" />
            <YAxis stroke="#94a3b8" />
            <Tooltip />
            <Bar dataKey="jobs" fill="#22d3ee" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
}

