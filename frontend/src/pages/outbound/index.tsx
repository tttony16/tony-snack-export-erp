import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Button } from 'antd';
import { listOutboundOrders } from '@/api/outbound';
import { OutboundOrderStatusLabels, OutboundOrderStatusColors } from '@/types/api';
import type { OutboundOrderListRead } from '@/types/models';
import { formatDateTime } from '@/utils/format';
import StatusTag from '@/components/StatusTag';

export default function OutboundOrdersPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();

  const columns: ProColumns<OutboundOrderListRead>[] = [
    {
      title: '出库单号',
      dataIndex: 'order_no',
      width: 180,
      render: (_, record) => (
        <a onClick={() => navigate(`/outbound/${record.id}`)}>{record.order_no}</a>
      ),
    },
    { title: '排柜计划ID', dataIndex: 'container_plan_id', ellipsis: true, hideInSearch: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueEnum: OutboundOrderStatusLabels,
      render: (_, record) => (
        <StatusTag
          value={record.status}
          statusMap={OutboundOrderStatusLabels}
          colorMap={OutboundOrderStatusColors}
        />
      ),
    },
    {
      title: '出库日期',
      dataIndex: 'outbound_date',
      width: 110,
      hideInSearch: true,
      render: (_, r) => r.outbound_date || '-',
    },
    { title: '操作员', dataIndex: 'operator', width: 100, hideInSearch: true, render: (v) => (v as string) || '-' },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      width: 170,
      hideInSearch: true,
      render: (_, r) => formatDateTime(r.created_at),
    },
    {
      title: '操作',
      width: 80,
      hideInSearch: true,
      render: (_, record) => (
        <Button type="link" size="small" onClick={() => navigate(`/outbound/${record.id}`)}>
          详情
        </Button>
      ),
    },
  ];

  return (
    <PageContainer>
      <ProTable<OutboundOrderListRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        request={async (params) => {
          const { current, pageSize, keyword, status, ...rest } = params;
          const data = await listOutboundOrders({
            page: current,
            page_size: pageSize,
            keyword,
            status,
            ...rest,
          });
          return { data: data.items, total: data.total, success: true };
        }}
        search={{ labelWidth: 'auto' }}
      />
    </PageContainer>
  );
}
