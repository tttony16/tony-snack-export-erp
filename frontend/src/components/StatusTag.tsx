import { Tag } from 'antd';

interface StatusTagProps<T extends string> {
  value: T;
  statusMap: Record<T, string>;
  colorMap?: Record<T, string>;
}

export default function StatusTag<T extends string>({
  value,
  statusMap,
  colorMap,
}: StatusTagProps<T>) {
  return (
    <Tag color={colorMap?.[value] || 'default'}>
      {statusMap[value] || value}
    </Tag>
  );
}
