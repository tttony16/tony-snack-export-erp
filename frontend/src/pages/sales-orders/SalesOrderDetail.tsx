import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '@ant-design/pro-components';
import { Descriptions, Table, Card, Space, Button, message, Spin } from 'antd';
import { getSalesOrder, confirmSalesOrder, generatePurchaseOrder } from '@/api/salesOrders';
import {
  SalesOrderStatusLabels,
  SalesOrderStatusColors,
  CurrencyTypeLabels,
  PaymentMethodLabels,
  TradeTermLabels,
  UnitTypeLabels,
} from '@/types/api';
import type { SalesOrderRead } from '@/types/models';
import { formatDate, formatDateTime, formatCurrency, formatEnum } from '@/utils/format';
import StatusTag from '@/components/StatusTag';
import PermissionButton from '@/components/PermissionButton';

export default function SalesOrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<SalesOrderRead>();
  const [loading, setLoading] = useState(true);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await getSalesOrder(id);
      setOrder(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading || !order) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  const handleConfirm = async () => {
    await confirmSalesOrder(order.id);
    message.success('确认成功');
    load();
  };

  const handleGeneratePO = async () => {
    await generatePurchaseOrder(order.id);
    message.success('采购单生成成功');
    load();
  };

  return (
    <PageContainer
      title={`销售订单 ${order.order_no}`}
      extra={
        <Space>
          {order.status === 'draft' && (
            <PermissionButton permission="sales_order:confirm" type="primary" onClick={handleConfirm}>
              确认订单
            </PermissionButton>
          )}
          {order.status === 'confirmed' && (
            <PermissionButton permission="sales_order:edit" type="primary" onClick={handleGeneratePO}>
              生成采购单
            </PermissionButton>
          )}
          <Button onClick={() => navigate('/sales-orders')}>返回列表</Button>
        </Space>
      }
    >
      <Card title="订单信息" style={{ marginBottom: 16 }}>
        <Descriptions column={3}>
          <Descriptions.Item label="订单号">{order.order_no}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <StatusTag value={order.status} statusMap={SalesOrderStatusLabels} colorMap={SalesOrderStatusColors} />
          </Descriptions.Item>
          <Descriptions.Item label="订单日期">{formatDate(order.order_date)}</Descriptions.Item>
          <Descriptions.Item label="要求交期">{formatDate(order.required_delivery_date)}</Descriptions.Item>
          <Descriptions.Item label="目的港">{order.destination_port}</Descriptions.Item>
          <Descriptions.Item label="贸易条款">{formatEnum(order.trade_term, TradeTermLabels)}</Descriptions.Item>
          <Descriptions.Item label="币种">{formatEnum(order.currency, CurrencyTypeLabels)}</Descriptions.Item>
          <Descriptions.Item label="付款方式">{formatEnum(order.payment_method, PaymentMethodLabels)}</Descriptions.Item>
          <Descriptions.Item label="付款条件">{order.payment_terms || '-'}</Descriptions.Item>
          <Descriptions.Item label="总金额">{formatCurrency(order.total_amount)}</Descriptions.Item>
          <Descriptions.Item label="总数量">{order.total_quantity}</Descriptions.Item>
          <Descriptions.Item label="备注">{order.remark || '-'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatDateTime(order.created_at)}</Descriptions.Item>
          <Descriptions.Item label="更新时间">{formatDateTime(order.updated_at)}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="订单明细">
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
            {
              title: '单价',
              dataIndex: 'unit_price',
              width: 100,
              render: (v) => formatCurrency(v as number),
            },
            {
              title: '金额',
              dataIndex: 'amount',
              width: 120,
              render: (v) => formatCurrency(v as number),
            },
            { title: '已采购', dataIndex: 'purchased_quantity', width: 80 },
            { title: '已收货', dataIndex: 'received_quantity', width: 80 },
          ]}
          summary={(data) => {
            const totalAmount = data.reduce((sum, item) => sum + Number(item.amount), 0);
            const totalQty = data.reduce((sum, item) => sum + item.quantity, 0);
            return (
              <Table.Summary.Row>
                <Table.Summary.Cell index={0}>合计</Table.Summary.Cell>
                <Table.Summary.Cell index={1}>{totalQty}</Table.Summary.Cell>
                <Table.Summary.Cell index={2} />
                <Table.Summary.Cell index={3} />
                <Table.Summary.Cell index={4}>{formatCurrency(totalAmount)}</Table.Summary.Cell>
                <Table.Summary.Cell index={5} />
                <Table.Summary.Cell index={6} />
              </Table.Summary.Row>
            );
          }}
        />
      </Card>
    </PageContainer>
  );
}
