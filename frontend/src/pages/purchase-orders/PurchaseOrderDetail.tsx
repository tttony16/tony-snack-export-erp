import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '@ant-design/pro-components';
import { Descriptions, Table, Card, Space, Button, message, Spin } from 'antd';
import {
  getPurchaseOrder,
  confirmPurchaseOrder,
  cancelPurchaseOrder,
} from '@/api/purchaseOrders';
import {
  PurchaseOrderStatusLabels,
  PurchaseOrderStatusColors,
  UnitTypeLabels,
} from '@/types/api';
import type { PurchaseOrderRead } from '@/types/models';
import { formatDate, formatDateTime, formatCurrency, formatEnum } from '@/utils/format';
import StatusTag from '@/components/StatusTag';
import PermissionButton from '@/components/PermissionButton';

export default function PurchaseOrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<PurchaseOrderRead>();
  const [loading, setLoading] = useState(true);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    try {
      setOrder(await getPurchaseOrder(id));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading || !order) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  return (
    <PageContainer
      title={`采购订单 ${order.order_no}`}
      extra={
        <Space>
          {order.status === 'draft' && (
            <PermissionButton
              permission="purchase_order:confirm"
              type="primary"
              onClick={async () => {
                await confirmPurchaseOrder(order.id);
                message.success('确认成功');
                load();
              }}
            >
              确认
            </PermissionButton>
          )}
          {order.status === 'draft' && (
            <PermissionButton
              permission="purchase_order:confirm"
              danger
              onClick={async () => {
                await cancelPurchaseOrder(order.id);
                message.success('已取消');
                load();
              }}
            >
              取消
            </PermissionButton>
          )}
          <Button onClick={() => navigate('/purchase-orders')}>返回列表</Button>
        </Space>
      }
    >
      <Card title="订单信息" style={{ marginBottom: 16 }}>
        <Descriptions column={3}>
          <Descriptions.Item label="采购单号">{order.order_no}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <StatusTag value={order.status} statusMap={PurchaseOrderStatusLabels} colorMap={PurchaseOrderStatusColors} />
          </Descriptions.Item>
          <Descriptions.Item label="订单日期">{formatDate(order.order_date)}</Descriptions.Item>
          <Descriptions.Item label="要求交期">{formatDate(order.required_date)}</Descriptions.Item>
          <Descriptions.Item label="总金额">{formatCurrency(order.total_amount)}</Descriptions.Item>
          <Descriptions.Item label="备注">{order.remark || '-'}</Descriptions.Item>
          <Descriptions.Item label="关联销售单">
            {order.linked_sales_order_ids.length > 0
              ? order.linked_sales_order_ids.map((id) => (
                  <a key={id} onClick={() => navigate(`/sales-orders/${id}`)} style={{ marginRight: 8 }}>
                    {id.substring(0, 8)}...
                  </a>
                ))
              : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatDateTime(order.created_at)}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{formatDateTime(order.updated_at)}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="采购明细">
        <Table
          dataSource={order.items}
          rowKey="id"
          pagination={false}
          columns={[
            { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
            { title: '数量', dataIndex: 'quantity', width: 80 },
            {
              title: '单位',
              dataIndex: 'unit',
              width: 60,
              render: (v) => formatEnum(v as string, UnitTypeLabels),
            },
            { title: '单价', dataIndex: 'unit_price', width: 100, render: (v) => formatCurrency(v as number) },
            { title: '金额', dataIndex: 'amount', width: 120, render: (v) => formatCurrency(v as number) },
            { title: '已收货', dataIndex: 'received_quantity', width: 80 },
          ]}
        />
      </Card>
    </PageContainer>
  );
}
