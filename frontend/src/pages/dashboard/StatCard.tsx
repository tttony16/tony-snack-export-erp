import { Card, Statistic } from 'antd';
import type { ReactNode } from 'react';

interface Props {
  icon: ReactNode;
  title: string;
  value: number;
  suffix?: string;
  onClick?: () => void;
}

export default function StatCard({ icon, title, value, suffix, onClick }: Props) {
  return (
    <Card
      hoverable={!!onClick}
      onClick={onClick}
      style={{ cursor: onClick ? 'pointer' : 'default' }}
    >
      <Statistic
        title={
          <span>
            {icon} <span style={{ marginLeft: 8 }}>{title}</span>
          </span>
        }
        value={value}
        suffix={suffix}
      />
    </Card>
  );
}
