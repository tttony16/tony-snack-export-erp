import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer } from '@ant-design/pro-components';
import { Row, Col, Card, List, Tag, Spin, Badge } from 'antd';
import {
  FileTextOutlined,
  ShoppingCartOutlined,
  CheckCircleOutlined,
  SendOutlined,
  WarningOutlined,
} from '@ant-design/icons';
import { getTodos, getInTransit, getExpiryWarnings } from '@/api/dashboard';
import type { TodoResponse, InTransitItem, ExpiryWarningItem } from '@/types/models';
import { formatDate } from '@/utils/format';
import StatCard from './StatCard';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [todos, setTodos] = useState<TodoResponse>();
  const [inTransit, setInTransit] = useState<InTransitItem[]>([]);
  const [warnings, setWarnings] = useState<ExpiryWarningItem[]>([]);

  useEffect(() => {
    Promise.all([
      getTodos().catch(() => null),
      getInTransit().catch(() => ({ items: [], total: 0 })),
      getExpiryWarnings().catch(() => ({ threshold: 0.5, items: [] })),
    ]).then(([todosData, transitData, warningData]) => {
      if (todosData) setTodos(todosData);
      setInTransit(transitData.items);
      setWarnings(warningData.items);
      setLoading(false);
    });
  }, []);

  if (loading) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <PageContainer title="工作台">
      {/* KPI Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={12} sm={6}>
          <StatCard
            icon={<FileTextOutlined />}
            title="待确认销售单"
            value={todos?.draft_sales_orders || 0}
            suffix="单"
            onClick={() => navigate('/sales-orders?status=draft')}
          />
        </Col>
        <Col xs={12} sm={6}>
          <StatCard
            icon={<ShoppingCartOutlined />}
            title="待收货采购单"
            value={todos?.ordered_purchase_orders || 0}
            suffix="单"
            onClick={() => navigate('/purchase-orders?status=ordered')}
          />
        </Col>
        <Col xs={12} sm={6}>
          <StatCard
            icon={<CheckCircleOutlined />}
            title="备货完成"
            value={todos?.goods_ready_sales_orders || 0}
            suffix="单"
            onClick={() => navigate('/sales-orders?status=goods_ready')}
          />
        </Col>
        <Col xs={12} sm={6}>
          <StatCard
            icon={<SendOutlined />}
            title="即将到港"
            value={todos?.arriving_soon_containers || 0}
            suffix="柜"
          />
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* In Transit */}
        <Col xs={24} lg={12}>
          <Card title="在途物流" size="small">
            <List
              dataSource={inTransit.slice(0, 8)}
              renderItem={(item) => (
                <List.Item
                  actions={[
                    <a key="view" onClick={() => navigate(`/logistics/${item.logistics_id}`)}>
                      查看
                    </a>,
                  ]}
                >
                  <List.Item.Meta
                    title={item.logistics_no}
                    description={
                      <>
                        {item.shipping_company && `${item.shipping_company} `}
                        {item.vessel_voyage && `${item.vessel_voyage} `}
                        <Tag>{item.status}</Tag>
                      </>
                    }
                  />
                  <div>{item.eta ? `ETA: ${formatDate(item.eta)}` : '-'}</div>
                </List.Item>
              )}
              locale={{ emptyText: '暂无在途物流' }}
            />
          </Card>
        </Col>

        {/* Expiry Warnings */}
        <Col xs={24} lg={12}>
          <Card
            title={
              <span>
                <WarningOutlined style={{ color: '#faad14' }} /> 保质期预警
              </span>
            }
            size="small"
          >
            <List
              dataSource={warnings.slice(0, 8)}
              renderItem={(item) => {
                const color =
                  item.remaining_ratio < 0.3 ? 'red' : item.remaining_ratio < 0.5 ? 'orange' : 'green';
                return (
                  <List.Item>
                    <List.Item.Meta
                      title={item.product_name || item.product_id}
                      description={`批次: ${item.batch_no} | 生产: ${formatDate(item.production_date)} | 数量: ${item.quantity}`}
                    />
                    <Badge
                      color={color}
                      text={`剩余 ${item.remaining_days} 天`}
                    />
                  </List.Item>
                );
              }}
              locale={{ emptyText: '暂无预警' }}
            />
          </Card>
        </Col>
      </Row>
    </PageContainer>
  );
}
