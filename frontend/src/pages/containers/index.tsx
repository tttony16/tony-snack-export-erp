import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { PlusOutlined } from '@ant-design/icons';
import { listContainerPlans } from '@/api/containers';
import { ContainerPlanStatusLabels, ContainerPlanStatusColors, ContainerTypeLabels } from '@/types/api';
import type { ContainerPlanListRead } from '@/types/models';
import { formatDate } from '@/utils/format';
import PermissionButton from '@/components/PermissionButton';
import StatusTag from '@/components/StatusTag';
import ContainerForm from './ContainerForm';

export default function ContainersPage() {
  const actionRef = useRef<ActionType>();
  const navigate = useNavigate();
  const [formOpen, setFormOpen] = useState(false);

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
    <PageContainer>
      <ProTable<ContainerPlanListRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
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
      <ContainerForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
      />
    </PageContainer>
  );
}
