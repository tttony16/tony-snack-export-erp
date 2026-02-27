import { useRef, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Segmented } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { listContainerPlans } from '@/api/containers';
import { ContainerPlanStatusLabels, ContainerPlanStatusColors, ContainerTypeLabels } from '@/types/api';
import type { ContainerPlanListRead } from '@/types/models';
import { formatDate } from '@/utils/format';
import PermissionButton from '@/components/PermissionButton';
import StatusTag from '@/components/StatusTag';
import ContainerForm from './ContainerForm';
import ContainerKanbanView from './ContainerKanbanView';

export default function ContainersPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [formOpen, setFormOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'list' | 'kanban'>('list');

  const columns: ProColumns<ContainerPlanListRead>[] = [
    { title: '计划号', dataIndex: 'plan_no', width: 140 },
    {
      title: '柜型',
      dataIndex: 'container_type',
      width: 100,
      valueEnum: ContainerTypeLabels,
    },
    { title: '柜数', dataIndex: 'container_count', width: 70, hideInSearch: true },
    { title: '目的港', dataIndex: 'destination_port', width: 120, hideInSearch: true },
    {
      title: '状态',
      dataIndex: 'status',
      width: 100,
      valueEnum: ContainerPlanStatusLabels,
      render: (_, r) => (
        <StatusTag value={r.status} statusMap={ContainerPlanStatusLabels} colorMap={ContainerPlanStatusColors} />
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      hideInSearch: true,
      width: 170,
      render: (_, r) => formatDate(r.created_at),
    },
    {
      title: '操作',
      valueType: 'option',
      width: 80,
      render: (_, record) => [
        <a key="view" onClick={() => navigate(`/containers/${record.id}`)}>详情</a>,
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
        <ContainerKanbanView />
      ) : (
        <ProTable<ContainerPlanListRead>
          actionRef={actionRef}
          rowKey="id"
          columns={columns}
          params={{ keyword: searchParams.get('keyword') || undefined }}
          request={async (params) => {
            const { current, pageSize, keyword, ...rest } = params;
            const data = await listContainerPlans({
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
              permission="container:edit"
              onClick={() => setFormOpen(true)}
            >
              新建排柜计划
            </PermissionButton>,
          ]}
        />
      )}
      <ContainerForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
      />
    </PageContainer>
  );
}
