import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Space } from 'antd';
import { PlusOutlined, DownloadOutlined } from '@ant-design/icons';
import { listCustomers } from '@/api/customers';
import { CurrencyTypeLabels, PaymentMethodLabels } from '@/types/api';
import type { CustomerRead } from '@/types/models';
import { formatDateTime } from '@/utils/format';
import { useExport } from '@/hooks/useExport';
import PermissionButton from '@/components/PermissionButton';
import CustomerForm from './CustomerForm';

export default function CustomersPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();
  const [formOpen, setFormOpen] = useState(false);
  const [editRecord, setEditRecord] = useState<CustomerRead | undefined>();
  const { exporting, handleExport } = useExport('/customers/export', '客户列表.xlsx');

  const columns: ProColumns<CustomerRead>[] = [
    { title: '客户编码', dataIndex: 'customer_code', width: 120 },
    { title: '客户名称', dataIndex: 'name', ellipsis: true },
    { title: '国家', dataIndex: 'country', width: 100 },
    { title: '联系人', dataIndex: 'contact_person', width: 100, hideInSearch: true },
    {
      title: '币种',
      dataIndex: 'currency',
      valueEnum: CurrencyTypeLabels,
      width: 120,
      hideInSearch: true,
    },
    {
      title: '付款方式',
      dataIndex: 'payment_method',
      valueEnum: PaymentMethodLabels,
      width: 100,
      hideInSearch: true,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      hideInSearch: true,
      width: 170,
      render: (_, r) => formatDateTime(r.created_at),
    },
    {
      title: '操作',
      valueType: 'option',
      width: 140,
      render: (_, record) => (
        <Space>
          <a onClick={() => { setEditRecord(record); setFormOpen(true); }}>编辑</a>
          <a onClick={() => navigate(`/sales-orders?customer_id=${record.id}`)}>查看订单</a>
        </Space>
      ),
    },
  ];

  return (
    <PageContainer>
      <ProTable<CustomerRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        request={async (params) => {
          const { current, pageSize, keyword, ...rest } = params;
          const data = await listCustomers({
            page: current,
            page_size: pageSize,
            keyword,
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
            permission="customer:edit"
            onClick={() => { setEditRecord(undefined); setFormOpen(true); }}
          >
            新建客户
          </PermissionButton>,
          <PermissionButton
            key="export"
            permission="customer:export"
            icon={<DownloadOutlined />}
            loading={exporting}
            onClick={() => handleExport()}
          >
            导出
          </PermissionButton>,
        ]}
      />
      <CustomerForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
        record={editRecord}
      />
    </PageContainer>
  );
}
