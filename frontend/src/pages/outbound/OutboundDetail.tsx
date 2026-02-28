import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '@ant-design/pro-components';
import { Descriptions, Table, Card, Space, Button, message, Spin, Modal, Form, Input, DatePicker } from 'antd';
import { getOutboundOrder, confirmOutboundOrder, cancelOutboundOrder } from '@/api/outbound';
import { OutboundOrderStatusLabels, OutboundOrderStatusColors } from '@/types/api';
import type { OutboundOrderRead } from '@/types/models';
import { formatDate, formatDateTime } from '@/utils/format';
import StatusTag from '@/components/StatusTag';
import PermissionButton from '@/components/PermissionButton';
import dayjs from 'dayjs';

export default function OutboundDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<OutboundOrderRead>();
  const [loading, setLoading] = useState(true);
  const [confirmModalOpen, setConfirmModalOpen] = useState(false);
  const [form] = Form.useForm();

  const load = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const data = await getOutboundOrder(id);
      setOrder(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading || !order) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  const handleConfirm = async () => {
    const values = await form.validateFields();
    await confirmOutboundOrder(order.id, {
      outbound_date: values.outbound_date.format('YYYY-MM-DD'),
      operator: values.operator,
    });
    message.success('出库确认成功');
    setConfirmModalOpen(false);
    load();
  };

  const handleCancel = async () => {
    Modal.confirm({
      title: '取消出库单',
      content: '确认取消此出库单？',
      onOk: async () => {
        await cancelOutboundOrder(order.id);
        message.success('已取消');
        load();
      },
    });
  };

  return (
    <PageContainer
      title={`出库单 ${order.order_no}`}
      extra={
        <Space>
          {order.status === 'draft' && (
            <>
              <PermissionButton
                permission="outbound:confirm"
                type="primary"
                onClick={() => setConfirmModalOpen(true)}
              >
                确认出库
              </PermissionButton>
              <PermissionButton permission="outbound:edit" danger onClick={handleCancel}>
                取消
              </PermissionButton>
            </>
          )}
          <Button onClick={() => navigate('/outbound')}>返回列表</Button>
        </Space>
      }
    >
      <Card title="出库单信息" style={{ marginBottom: 16 }}>
        <Descriptions column={3}>
          <Descriptions.Item label="单号">{order.order_no}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <StatusTag
              value={order.status}
              statusMap={OutboundOrderStatusLabels}
              colorMap={OutboundOrderStatusColors}
            />
          </Descriptions.Item>
          <Descriptions.Item label="排柜计划ID">{order.container_plan_id}</Descriptions.Item>
          <Descriptions.Item label="出库日期">{order.outbound_date || '-'}</Descriptions.Item>
          <Descriptions.Item label="操作员">{order.operator || '-'}</Descriptions.Item>
          <Descriptions.Item label="备注">{order.remark || '-'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatDateTime(order.created_at)}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card title="出库明细">
        <Table
          dataSource={order.items}
          rowKey="id"
          pagination={false}
          columns={[
            { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
            { title: '批次号', dataIndex: 'batch_no', width: 130 },
            {
              title: '生产日期',
              dataIndex: 'production_date',
              width: 110,
              render: (v) => formatDate(v as string),
            },
            { title: '数量', dataIndex: 'quantity', width: 80 },
            {
              title: '关联订单ID',
              dataIndex: 'sales_order_id',
              ellipsis: true,
              render: (v) => (v as string) || '-',
            },
          ]}
        />
      </Card>

      <Modal
        title="确认出库"
        open={confirmModalOpen}
        onOk={handleConfirm}
        onCancel={() => setConfirmModalOpen(false)}
        okText="确认"
        cancelText="取消"
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="outbound_date"
            label="出库日期"
            rules={[{ required: true, message: '请选择出库日期' }]}
            initialValue={dayjs()}
          >
            <DatePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item
            name="operator"
            label="操作员"
            rules={[{ required: true, message: '请输入操作员' }]}
          >
            <Input placeholder="请输入操作员姓名" />
          </Form.Item>
        </Form>
      </Modal>
    </PageContainer>
  );
}
