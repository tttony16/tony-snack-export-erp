import { useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Button, Switch, message } from 'antd';
import { PlusOutlined, UploadOutlined, DownloadOutlined } from '@ant-design/icons';
import { listProducts, listBrands, updateProductStatus, importProducts } from '@/api/products';
import { ProductStatusLabels } from '@/types/api';
import type { ProductRead } from '@/types/models';
import { formatDateTime } from '@/utils/format';
import { useExport } from '@/hooks/useExport';
import { downloadFile } from '@/utils/download';
import PermissionButton from '@/components/PermissionButton';
import CategoryCascader from '@/components/CategoryCascader';
import ProductForm from './ProductForm';

export default function ProductsPage() {
  const actionRef = useRef<ActionType>();
  const [searchParams] = useSearchParams();
  const [formOpen, setFormOpen] = useState(false);
  const [editRecord, setEditRecord] = useState<ProductRead | undefined>();
  const { exporting, handleExport } = useExport('/products/export', '商品列表.xlsx');

  const columns: ProColumns<ProductRead>[] = [
    {
      title: '关键词',
      dataIndex: 'keyword',
      hideInTable: true,
      fieldProps: { placeholder: '搜索 SKU / 名称' },
    },
    { title: 'SKU', dataIndex: 'sku_code', width: 140, hideInSearch: true },
    { title: '中文名称', dataIndex: 'name_cn', ellipsis: true, hideInSearch: true },
    { title: '英文名称', dataIndex: 'name_en', ellipsis: true, hideInSearch: true },
    {
      title: '分类',
      dataIndex: 'category_id',
      width: 180,
      render: (_, record) => {
        const parts = [
          record.category_level1_name,
          record.category_level2_name,
          record.category_level3_name,
        ].filter(Boolean);
        return parts.join(' / ') || '-';
      },
      renderFormItem: (_, { value, onChange }) => (
        <CategoryCascader
          allowAnyLevel
          placeholder="按品类筛选"
          value={value}
          onChange={onChange}
        />
      ),
    },
    {
      title: '品牌',
      dataIndex: 'brand',
      width: 100,
      valueType: 'select',
      request: async () => {
        const brands = await listBrands();
        return brands.map((b) => ({ value: b, label: b }));
      },
    },
    { title: '规格', dataIndex: 'spec', width: 120, hideInSearch: true },
    {
      title: '状态',
      dataIndex: 'status',
      valueEnum: ProductStatusLabels,
      width: 80,
      render: (_, record) => (
        <Switch
          checked={record.status === 'active'}
          checkedChildren="启用"
          unCheckedChildren="停用"
          onChange={async (checked) => {
            await updateProductStatus(record.id, checked ? 'active' : 'inactive');
            message.success('状态更新成功');
            actionRef.current?.reload();
          }}
        />
      ),
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
      width: 80,
      render: (_, record) => [
        <a
          key="edit"
          onClick={() => {
            setEditRecord(record);
            setFormOpen(true);
          }}
        >
          编辑
        </a>,
      ],
    },
  ];

  return (
    <PageContainer>
      <ProTable<ProductRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        params={{ keyword: searchParams.get('keyword') || undefined }}
        request={async (params) => {
          const { current, pageSize, ...rest } = params;
          const data = await listProducts({
            page: current,
            page_size: pageSize,
            ...rest,
          });
          return { data: data.items, total: data.total, success: true };
        }}
        search={{ labelWidth: 'auto', defaultCollapsed: false }}
        scroll={{ x: 1200 }}
        toolBarRender={() => [
          <PermissionButton
            key="add"
            type="primary"
            icon={<PlusOutlined />}
            permission="product:edit"
            onClick={() => {
              setEditRecord(undefined);
              setFormOpen(true);
            }}
          >
            新建商品
          </PermissionButton>,
          <PermissionButton
            key="import"
            permission="product:import"
            icon={<UploadOutlined />}
            onClick={() => {
              // trigger file upload
              const input = document.createElement('input');
              input.type = 'file';
              input.accept = '.xlsx,.xls';
              input.onchange = async (e) => {
                const file = (e.target as HTMLInputElement).files?.[0];
                if (file) {
                  await importProducts(file);
                  message.success('导入成功');
                  actionRef.current?.reload();
                }
              };
              input.click();
            }}
          >
            导入
          </PermissionButton>,
          <PermissionButton
            key="export"
            permission="product:export"
            icon={<DownloadOutlined />}
            loading={exporting}
            onClick={() => handleExport()}
          >
            导出
          </PermissionButton>,
          <Button
            key="template"
            icon={<DownloadOutlined />}
            onClick={() => downloadFile('/api/v1/products/template', '商品导入模板.xlsx')}
          >
            下载模板
          </Button>,
        ]}
      />
      <ProductForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => {
          setFormOpen(false);
          actionRef.current?.reload();
        }}
        record={editRecord}
      />
    </PageContainer>
  );
}
