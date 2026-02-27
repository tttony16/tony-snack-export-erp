import { useRef } from 'react';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Tabs, Tag } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { listInventory } from '@/api/warehouse';
import type { InventoryByProductRead } from '@/types/models';
import { useExport } from '@/hooks/useExport';
import PermissionButton from '@/components/PermissionButton';

export default function InventoryPage() {
  const actionRef = useRef<ActionType>();
  const { exporting, handleExport } = useExport('/warehouse/inventory/export', '库存.xlsx');

  const productColumns: ProColumns<InventoryByProductRead>[] = [
    { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
    { title: '总数量', dataIndex: 'total_quantity', width: 100 },
    { title: '可用数量', dataIndex: 'available_quantity', width: 100 },
    {
      title: '状态',
      hideInSearch: true,
      width: 80,
      render: (_, r) =>
        r.available_quantity > 0
          ? <Tag color="green">有库存</Tag>
          : <Tag color="default">无库存</Tag>,
    },
  ];

  return (
    <PageContainer>
      <Tabs
        items={[
          {
            key: 'by-product',
            label: '按商品汇总',
            children: (
              <ProTable<InventoryByProductRead>
                actionRef={actionRef}
                rowKey="product_id"
                columns={productColumns}
                request={async (params) => {
                  const { current, pageSize, keyword, ...rest } = params;
                  const data = await listInventory({
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
                    key="export"
                    permission="inventory:view"
                    icon={<DownloadOutlined />}
                    loading={exporting}
                    onClick={() => handleExport()}
                  >
                    导出
                  </PermissionButton>,
                ]}
              />
            ),
          },
          {
            key: 'by-order',
            label: '按订单查看',
            children: (
              <div style={{ padding: 24, color: '#999' }}>
                请在销售订单详情中查看按订单库存和齐货检查
              </div>
            ),
          },
        ]}
      />
    </PageContainer>
  );
}
