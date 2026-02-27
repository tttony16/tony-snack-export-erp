import { useState, useEffect } from 'react';
import { Card, Col, Row, Statistic, Spin } from 'antd';
import { listContainerPlans } from '@/api/containers';
import { ContainerPlanStatusLabels, ContainerPlanStatusColors } from '@/types/api';
import type { ContainerPlanListRead } from '@/types/models';

export default function ContainerKanbanView() {
  const [loading, setLoading] = useState(true);
  const [countMap, setCountMap] = useState<Record<string, number>>({});

  useEffect(() => {
    listContainerPlans({ page: 1, page_size: 1000 })
      .then((data) => {
        const map: Record<string, number> = {};
        data.items.forEach((item: ContainerPlanListRead) => {
          map[item.status] = (map[item.status] || 0) + 1;
        });
        setCountMap(map);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <Spin />;

  const allStatuses = Object.keys(ContainerPlanStatusLabels) as Array<keyof typeof ContainerPlanStatusLabels>;

  return (
    <Row gutter={[12, 12]}>
      {allStatuses.map((status) => {
        const count = countMap[status] || 0;
        const color = ContainerPlanStatusColors[status] || 'default';
        return (
          <Col key={status} xs={12} sm={8} md={6}>
            <Card size="small" style={{ borderTop: `3px solid ${color === 'default' ? '#d9d9d9' : color}` }}>
              <Statistic
                title={ContainerPlanStatusLabels[status]}
                value={count}
                suffix="个计划"
              />
            </Card>
          </Col>
        );
      })}
    </Row>
  );
}
