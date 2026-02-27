import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Space, Tag } from 'antd';
import { PlusOutlined, DownloadOutlined } from '@ant-design/icons';
import { listSuppliers } from '@/api/suppliers';
import { ProductCategoryLabels } from '@/types/api';
import type { ProductCategory } from '@/types/api';
import type { SupplierRead } from '@/types/models';
import { formatDateTime } from '@/utils/format';
import { useExport } from '@/hooks/useExport';
import PermissionButton from '@/components/PermissionButton';
import SupplierForm from './SupplierForm';
import SupplierProducts from './SupplierProducts';

export default function SuppliersPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();
  const [formOpen, setFormOpen] = useState(false);
  const [editRecord, setEditRecord] = useState<SupplierRead | undefined>();
  const [productsOpen, setProductsOpen] = useState(false);
  const [selectedSupplier, setSelectedSupplier] = useState<SupplierRead>();
  const { exporting, handleExport } = useExport('/suppliers/export', '供应商列表.xlsx');

  const columns: ProColumns<SupplierRead>[] = [
    { title: '供应商编码', dataIndex: 'supplier_code', width: 120 },
    { title: '供应商名称', dataIndex: 'name', ellipsis: true },
    { title: '联系人', dataIndex: 'contact_person', width: 100, hideInSearch: true },
    { title: '电话', dataIndex: 'phone', width: 130, hideInSearch: true },
    {
      title: '供应品类',
      dataIndex: 'supply_categories',
      hideInSearch: true,
      render: (_, record) =>
        record.supply_categories?.map((c) => (
          <Tag key={c}>{ProductCategoryLabels[c as ProductCategory] || c}</Tag>
        )) || '-',
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
      width: 200,
      render: (_, record) => (
        <Space>
          <a onClick={() => { setEditRecord(record); setFormOpen(true); }}>编辑</a>
          <a onClick={() => { setSelectedSupplier(record); setProductsOpen(true); }}>供应商品</a>
          <a onClick={() => navigate(`/purchase-orders?supplier_id=${record.id}`)}>采购单</a>
        </Space>
      ),
    },
  ];

  return (
    <PageContainer>
      <ProTable<SupplierRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        request={async (params) => {
          const { current, pageSize, keyword, ...rest } = params;
          const data = await listSuppliers({
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
            permission="supplier:edit"
            onClick={() => { setEditRecord(undefined); setFormOpen(true); }}
          >
            新建供应商
          </PermissionButton>,
          <PermissionButton
            key="export"
            permission="supplier:export"
            icon={<DownloadOutlined />}
            loading={exporting}
            onClick={() => handleExport()}
          >
            导出
          </PermissionButton>,
        ]}
      />
      <SupplierForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
        record={editRecord}
      />
      {selectedSupplier && (
        <SupplierProducts
          open={productsOpen}
          onClose={() => setProductsOpen(false)}
          supplierId={selectedSupplier.id}
          supplierName={selectedSupplier.name}
        />
      )}
    </PageContainer>
  );
}
