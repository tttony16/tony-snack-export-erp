import { useState, useEffect } from 'react';
import { Card, Col, Row, Statistic, Spin } from 'antd';
import { getSalesOrderKanban } from '@/api/salesOrders';
import { SalesOrderStatusLabels, SalesOrderStatusColors } from '@/types/api';
import type { KanbanItem } from '@/types/models';
import { formatCurrency } from '@/utils/format';

export default function KanbanView() {
  const [items, setItems] = useState<KanbanItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSalesOrderKanban()
      .then((data) => setItems(data.items || []))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  // Ensure all statuses are shown
  const allStatuses = Object.keys(SalesOrderStatusLabels) as Array<keyof typeof SalesOrderStatusLabels>;
  const itemMap = new Map(items.map((i) => [i.status, i]));

  return (
    <Row gutter={[12, 12]}>
      {allStatuses.map((status) => {
        const item = itemMap.get(status);
        const color = SalesOrderStatusColors[status] || 'default';
        return (
          <Col key={status} xs={12} sm={8} md={6} lg={4}>
            <Card size="small" style={{ borderTop: `3px solid ${color === 'default' ? '#d9d9d9' : color}` }}>
              <Statistic
                title={SalesOrderStatusLabels[status]}
                value={item?.count || 0}
                suffix="单"
              />
              <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                {formatCurrency(item?.total_amount || 0)}
              </div>
            </Card>
          </Col>
        );
      })}
    </Row>
  );
}
