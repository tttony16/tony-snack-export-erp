import { useState, useEffect } from 'react';
import { Card, Col, Row, Statistic, Spin } from 'antd';
import { getLogisticsKanban } from '@/api/logistics';
import { LogisticsStatusLabels, LogisticsStatusColors } from '@/types/api';
import type { LogisticsKanbanItem } from '@/types/models';
import { formatCurrency } from '@/utils/format';

export default function LogisticsKanbanView() {
  const [items, setItems] = useState<LogisticsKanbanItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getLogisticsKanban()
      .then((data) => setItems(data.items || []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  const allStatuses = Object.keys(LogisticsStatusLabels) as Array<keyof typeof LogisticsStatusLabels>;
  const itemMap = new Map(items.map((i) => [i.status, i]));

  return (
    <Row gutter={[12, 12]}>
      {allStatuses.map((status) => {
        const item = itemMap.get(status);
        const color = LogisticsStatusColors[status] || 'default';
        return (
          <Col key={status} xs={12} sm={8} md={6}>
            <Card size="small" style={{ borderTop: `3px solid ${color === 'default' ? '#d9d9d9' : color}` }}>
              <Statistic
                title={LogisticsStatusLabels[status]}
                value={item?.count || 0}
                suffix="单"
              />
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                费用: {formatCurrency(item?.total_cost || 0)}
              </div>
            </Card>
          </Col>
        );
      })}
    </Row>
  );
}
