import { useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Segmented } from 'antd';
import { PlusOutlined, DownloadOutlined } from '@ant-design/icons';
import { listSalesOrders } from '@/api/salesOrders';
import { SalesOrderStatusLabels, SalesOrderStatusColors } from '@/types/api';
import type { SalesOrderListRead } from '@/types/models';
import { formatDate, formatCurrency } from '@/utils/format';
import { useExport } from '@/hooks/useExport';
import PermissionButton from '@/components/PermissionButton';
import StatusTag from '@/components/StatusTag';
import SalesOrderForm from './SalesOrderForm';
import KanbanView from './KanbanView';

export default function SalesOrdersPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formOpen, setFormOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'kanban'>('list');
  const { exporting, handleExport } = useExport('/sales-orders/export', '销售订单.xlsx');

  const columns: ProColumns<SalesOrderListRead>[] = [
    { title: '订单号', dataIndex: 'order_no', width: 140 },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueEnum: SalesOrderStatusLabels,
      render: (_, r) => (
        <StatusTag value={r.status} statusMap={SalesOrderStatusLabels} colorMap={SalesOrderStatusColors} />
      ),
    },
    {
      title: '订单日期',
      dataIndex: 'order_date',
      hideInSearch: true,
      width: 110,
      render: (_, r) => formatDate(r.order_date),
    },
    {
      title: '交期',
      dataIndex: 'required_delivery_date',
      hideInSearch: true,
      width: 110,
      render: (_, r) => formatDate(r.required_delivery_date),
    },
    { title: '目的港', dataIndex: 'destination_port', width: 120, hideInSearch: true },
    { title: '贸易条款', dataIndex: 'trade_term', width: 80, hideInSearch: true },
    {
      title: '金额',
      dataIndex: 'total_amount',
      hideInSearch: true,
      width: 120,
      render: (_, r) => formatCurrency(r.total_amount, r.currency),
    },
    { title: '数量', dataIndex: 'total_quantity', hideInSearch: true, width: 80 },
    {
      title: '日期范围',
      dataIndex: 'dateRange',
      hideInTable: true,
      valueType: 'dateRange',
      search: {
        transform: (value) => ({ date_from: value[0], date_to: value[1] }),
      },
    },
    {
      title: '操作',
      valueType: 'option',
      width: 80,
      render: (_, record) => [
        <a key="view" onClick={() => navigate(`/sales-orders/${record.id}`)}>详情</a>,
      ],
    },
  ];

  return (
    <PageContainer
      extra={
        <Segmented
          options={[
            { label: '列表', value: 'list' },
            { label: '看板', value: 'kanban' },
          ]}
          value={viewMode}
          onChange={(v) => setViewMode(v as 'list' | 'kanban')}
        />
      }
    >
      {viewMode === 'kanban' ? (
        <KanbanView />
      ) : (
        <ProTable<SalesOrderListRead>
          actionRef={actionRef}
          rowKey="id"
          columns={columns}
          params={{ customer_id: searchParams.get('customer_id') || undefined }}
          request={async (params) => {
            const { current, pageSize, keyword, customer_id, ...rest } = params;
            const data = await listSalesOrders({
              page: current,
              page_size: pageSize,
              keyword,
              customer_id,
              ...rest,
            });
            return { data: data.items, total: data.total, success: true };
          }}
          search={{ labelWidth: 'auto' }}
          toolBarRender={() => [
            <PermissionButton
              key="add"
              type="primary"
              icon={<PlusOutlined />}
              permission="sales_order:edit"
              onClick={() => setFormOpen(true)}
            >
              新建订单
            </PermissionButton>,
            <PermissionButton
              key="export"
              permission="sales_order:export"
              icon={<DownloadOutlined />}
              loading={exporting}
              onClick={() => handleExport()}
            >
              导出
            </PermissionButton>,
          ]}
        />
      )}
      <SalesOrderForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
      />
    </PageContainer>
  );
}
