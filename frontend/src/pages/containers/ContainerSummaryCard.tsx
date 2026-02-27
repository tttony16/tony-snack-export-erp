import { Card, Progress, Space, Typography } from 'antd';
import type { ContainerSummaryItem } from '@/types/models';
import { formatDecimal } from '@/utils/format';

const { Text } = Typography;

interface Props {
  item: ContainerSummaryItem;
}

export default function ContainerSummaryCard({ item }: Props) {
  const volumePercent = Number(item.volume_utilization);
  const weightPercent = Number(item.weight_utilization);

  return (
    <Card size="small" title={`柜 #${item.container_seq}`} style={{ marginBottom: 12 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text type="secondary">体积利用率</Text>
          <Progress
            percent={Math.min(volumePercent, 100)}
            status={item.is_over_volume ? 'exception' : 'normal'}
            format={() => `${formatDecimal(volumePercent)}%`}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatDecimal(Number(item.loaded_volume_cbm))} cbm
          </Text>
        </div>
        <div>
          <Text type="secondary">重量利用率</Text>
          <Progress
            percent={Math.min(weightPercent, 100)}
            status={item.is_over_weight ? 'exception' : 'normal'}
            format={() => `${formatDecimal(weightPercent)}%`}
          />
          <Text type="secondary" style={{ fontSize: 12 }}>
            {formatDecimal(Number(item.loaded_weight_kg))} kg
          </Text>
        </div>
        <Text type="secondary" style={{ fontSize: 12 }}>
          {item.item_count} 项货品
        </Text>
      </Space>
    </Card>
  );
}
