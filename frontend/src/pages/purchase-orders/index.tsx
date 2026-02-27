import { useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { PlusOutlined } from '@ant-design/icons';
import { listPurchaseOrders } from '@/api/purchaseOrders';
import { PurchaseOrderStatusLabels, PurchaseOrderStatusColors } from '@/types/api';
import type { PurchaseOrderListRead } from '@/types/models';
import { formatDate, formatCurrency } from '@/utils/format';
import PermissionButton from '@/components/PermissionButton';
import StatusTag from '@/components/StatusTag';
import PurchaseOrderForm from './PurchaseOrderForm';

export default function PurchaseOrdersPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formOpen, setFormOpen] = useState(false);

  const columns: ProColumns<PurchaseOrderListRead>[] = [
    { title: '采购单号', dataIndex: 'order_no', width: 140 },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueEnum: PurchaseOrderStatusLabels,
      render: (_, r) => (
        <StatusTag value={r.status} statusMap={PurchaseOrderStatusLabels} colorMap={PurchaseOrderStatusColors} />
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
      title: '要求交期',
      dataIndex: 'required_date',
      hideInSearch: true,
      width: 110,
      render: (_, r) => formatDate(r.required_date),
    },
    {
      title: '金额',
      dataIndex: 'total_amount',
      hideInSearch: true,
      width: 120,
      render: (_, r) => formatCurrency(r.total_amount),
    },
    {
      title: '操作',
      valueType: 'option',
      width: 80,
      render: (_, record) => [
        <a key="view" onClick={() => navigate(`/purchase-orders/${record.id}`)}>详情</a>,
      ],
    },
  ];

  return (
    <PageContainer>
      <ProTable<PurchaseOrderListRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        params={{ supplier_id: searchParams.get('supplier_id') || undefined, keyword: searchParams.get('keyword') || undefined }}
        request={async (params) => {
          const { current, pageSize, keyword, supplier_id, ...rest } = params;
          const data = await listPurchaseOrders({
            page: current,
            page_size: pageSize,
            keyword,
            supplier_id,
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
            permission="purchase_order:edit"
            onClick={() => setFormOpen(true)}
          >
            新建采购单
          </PermissionButton>,
        ]}
      />
      <PurchaseOrderForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
      />
    </PageContainer>
  );
}
