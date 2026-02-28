import { useRef, useState } from 'react';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Tabs, Tag, Alert, Space, Button, Table } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { listInventory, getInventoryByOrder, checkReadiness, listPendingInspection, listInventoryBatches } from '@/api/warehouse';
import { listSalesOrders } from '@/api/salesOrders';
import { InspectionResultLabels, InspectionResultColors } from '@/types/api';
import type { InventoryByProductRead, InventoryByOrderRead, InventoryBatchRead, ReceivingNoteItemRead, ReadinessCheckResponse } from '@/types/models';
import { formatDate } from '@/utils/format';
import { useExport } from '@/hooks/useExport';
import PermissionButton from '@/components/PermissionButton';
import StatusTag from '@/components/StatusTag';
import EntitySelect from '@/components/EntitySelect';

function ByOrderTab() {
  const [selectedOrderId, setSelectedOrderId] = useState<string>();
  const [orderItems, setOrderItems] = useState<InventoryByOrderRead[]>([]);
  const [readiness, setReadiness] = useState<ReadinessCheckResponse | null>(null);
  const [loadingQuery, setLoadingQuery] = useState(false);
  const [loadingCheck, setLoadingCheck] = useState(false);

  const handleQuery = async () => {
    if (!selectedOrderId) return;
    setLoadingQuery(true);
    setReadiness(null);
    try {
      const data = await getInventoryByOrder(selectedOrderId);
      setOrderItems(data);
    } finally {
      setLoadingQuery(false);
    }
  };

  const handleReadinessCheck = async () => {
    if (!selectedOrderId) return;
    setLoadingCheck(true);
    try {
      const result = await checkReadiness(selectedOrderId);
      setReadiness(result);
    } finally {
      setLoadingCheck(false);
    }
  };

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <EntitySelect
          fetchFn={listSalesOrders}
          labelField="order_no"
          placeholder="选择销售订单"
          style={{ width: 300 }}
          value={selectedOrderId}
          onChange={(v) => setSelectedOrderId(v as string)}
          allowClear
        />
        <Button type="primary" onClick={handleQuery} loading={loadingQuery} disabled={!selectedOrderId}>
          查询
        </Button>
        <Button onClick={handleReadinessCheck} loading={loadingCheck} disabled={!selectedOrderId}>
          齐货检查
        </Button>
      </Space>

      {readiness && (
        <Alert
          type={readiness.is_ready ? 'success' : 'warning'}
          message={readiness.is_ready ? '齐货完成，可以安排装柜' : '尚未齐货，部分商品库存不足'}
          closable
          onClose={() => setReadiness(null)}
          style={{ marginBottom: 16 }}
        />
      )}

      <Table<InventoryByOrderRead>
        dataSource={orderItems}
        rowKey="product_id"
        pagination={false}
        columns={[
          { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
          { title: '总数量', dataIndex: 'total_quantity', width: 100 },
          { title: '可用数量', dataIndex: 'available_quantity', width: 100 },
        ]}
      />
    </div>
  );
}

function BatchDetailTab() {
  const [batches, setBatches] = useState<InventoryBatchRead[]>([]);
  const [loading, setLoading] = useState(false);

  const handleLoad = async () => {
    setLoading(true);
    try {
      const data = await listInventoryBatches({ page_size: 200 });
      setBatches(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Button type="primary" onClick={handleLoad} loading={loading} style={{ marginBottom: 16 }}>
        加载批次明细
      </Button>
      <Table<InventoryBatchRead>
        dataSource={batches}
        rowKey="id"
        loading={loading}
        pagination={{ pageSize: 20 }}
        columns={[
          { title: '商品名称', dataIndex: 'product_name', width: 150, ellipsis: true },
          { title: '关联订单', dataIndex: 'sales_order_no', width: 140 },
          { title: '批次号', dataIndex: 'batch_no', width: 130 },
          { title: '生产日期', dataIndex: 'production_date', width: 110, render: (v) => formatDate(v as string) },
          { title: '总量', dataIndex: 'quantity', width: 80 },
          { title: '预留量', dataIndex: 'reserved_quantity', width: 80 },
          { title: '可用量', dataIndex: 'available_quantity', width: 80 },
          {
            title: '保质期剩余',
            dataIndex: 'shelf_life_remaining_days',
            width: 100,
            render: (v: number | null) =>
              v !== null ? (
                <Tag color={v < 90 ? 'red' : v < 180 ? 'orange' : 'green'}>{v}天</Tag>
              ) : '-',
          },
        ]}
      />
    </div>
  );
}

export default function InventoryPage() {
  const actionRef = useRef<ActionType>();
  const inspectionActionRef = useRef<ActionType>();
  const { exporting, handleExport } = useExport('/warehouse/inventory/export', '库存.xlsx');

  const productColumns: ProColumns<InventoryByProductRead>[] = [
    { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
    { title: '总数量', dataIndex: 'total_quantity', width: 100 },
    { title: '已预留', dataIndex: 'reserved_quantity', width: 100 },
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

  const inspectionColumns: ProColumns<ReceivingNoteItemRead>[] = [
    { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
    { title: '批次号', dataIndex: 'batch_no', width: 140 },
    { title: '应收数量', dataIndex: 'expected_quantity', width: 100, hideInSearch: true },
    { title: '实收数量', dataIndex: 'actual_quantity', width: 100, hideInSearch: true },
    {
      title: '验货结果',
      dataIndex: 'inspection_result',
      width: 100,
      hideInSearch: true,
      render: (_, r) => (
        <StatusTag value={r.inspection_result} statusMap={InspectionResultLabels} colorMap={InspectionResultColors} />
      ),
    },
    {
      title: '生产日期',
      dataIndex: 'production_date',
      width: 110,
      hideInSearch: true,
      render: (_, r) => formatDate(r.production_date),
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
            children: <ByOrderTab />,
          },
          {
            key: 'batch-detail',
            label: '库存批次明细',
            children: <BatchDetailTab />,
          },
          {
            key: 'pending-inspection',
            label: '待验货',
            children: (
              <ProTable<ReceivingNoteItemRead>
                actionRef={inspectionActionRef}
                rowKey="id"
                columns={inspectionColumns}
                request={async (params) => {
                  const { current, pageSize, keyword, ...rest } = params;
                  const data = await listPendingInspection({
                    page: current,
                    page_size: pageSize,
                    keyword,
                    ...rest,
                  });
                  return { data: data.items, total: data.total, success: true };
                }}
                search={{ labelWidth: 'auto' }}
              />
            ),
          },
        ]}
      />
    </PageContainer>
  );
}
