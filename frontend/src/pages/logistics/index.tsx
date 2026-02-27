import { useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Segmented } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { listLogistics } from '@/api/logistics';
import { LogisticsStatusLabels, LogisticsStatusColors } from '@/types/api';
import type { LogisticsRecordListRead } from '@/types/models';
import { formatDate, formatCurrency } from '@/utils/format';
import PermissionButton from '@/components/PermissionButton';
import StatusTag from '@/components/StatusTag';
import LogisticsForm from './LogisticsForm';
import LogisticsKanbanView from './LogisticsKanbanView';

export default function LogisticsPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formOpen, setFormOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'kanban'>('list');

  const columns: ProColumns<LogisticsRecordListRead>[] = [
    { title: '物流编号', dataIndex: 'logistics_no', width: 140 },
    { title: '船公司', dataIndex: 'shipping_company', width: 120, hideInSearch: true },
    { title: '船名航次', dataIndex: 'vessel_voyage', width: 140, hideInSearch: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueEnum: LogisticsStatusLabels,
      render: (_, r) => (
        <StatusTag value={r.status} statusMap={LogisticsStatusLabels} colorMap={LogisticsStatusColors} />
      ),
    },
    { title: 'ETD', dataIndex: 'etd', width: 110, hideInSearch: true, render: (_, r) => formatDate(r.etd) },
    { title: 'ETA', dataIndex: 'eta', width: 110, hideInSearch: true, render: (_, r) => formatDate(r.eta) },
    { title: '装港', dataIndex: 'port_of_loading', width: 100, hideInSearch: true },
    { title: '卸港', dataIndex: 'port_of_discharge', width: 100, hideInSearch: true },
    {
      title: '总费用',
      dataIndex: 'total_cost',
      hideInSearch: true,
      width: 100,
      render: (_, r) => formatCurrency(r.total_cost),
    },
    {
      title: '操作',
      valueType: 'option',
      width: 80,
      render: (_, record) => [
        <a key="view" onClick={() => navigate(`/logistics/${record.id}`)}>详情</a>,
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
        <LogisticsKanbanView />
      ) : (
        <ProTable<LogisticsRecordListRead>
          actionRef={actionRef}
          rowKey="id"
          columns={columns}
          params={{ keyword: searchParams.get('keyword') || undefined }}
          request={async (params) => {
            const { current, pageSize, keyword, ...rest } = params;
            const data = await listLogistics({
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
              permission="logistics:edit"
              onClick={() => setFormOpen(true)}
            >
              新建物流记录
            </PermissionButton>,
          ]}
        />
      )}
      <LogisticsForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
      />
    </PageContainer>
  );
}
