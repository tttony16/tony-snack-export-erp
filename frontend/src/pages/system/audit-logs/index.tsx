import { useRef } from 'react';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { listAuditLogs } from '@/api/system';
import { AuditActionLabels } from '@/types/api';
import type { AuditLogRead } from '@/types/models';
import { formatDateTime } from '@/utils/format';
import StatusTag from '@/components/StatusTag';

export default function AuditLogsPage() {
  const actionRef = useRef<ActionType>();

  const columns: ProColumns<AuditLogRead>[] = [
    { title: 'ID', dataIndex: 'id', width: 60, hideInSearch: true },
    {
      title: '操作类型',
      dataIndex: 'action',
      width: 100,
      valueEnum: AuditActionLabels,
      render: (_, record) => (
        <StatusTag value={record.action} statusMap={AuditActionLabels} />
      ),
    },
    { title: '资源类型', dataIndex: 'resource_type', width: 120 },
    { title: '资源ID', dataIndex: 'resource_id', width: 200, ellipsis: true, hideInSearch: true },
    {
      title: '详情',
      dataIndex: 'detail',
      hideInSearch: true,
      ellipsis: true,
      render: (_, r) => r.detail ? JSON.stringify(r.detail) : '-',
    },
    { title: 'IP地址', dataIndex: 'ip_address', width: 130, hideInSearch: true },
    {
      title: '操作时间',
      dataIndex: 'created_at',
      width: 170,
      valueType: 'dateRange',
      render: (_, r) => formatDateTime(r.created_at),
      search: {
        transform: (value) => ({
          date_from: value[0],
          date_to: value[1],
        }),
      },
    },
  ];

  return (
    <PageContainer>
      <ProTable<AuditLogRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        request={async (params) => {
          const { current, pageSize, ...rest } = params;
          const data = await listAuditLogs({
            page: current,
            page_size: pageSize,
            ...rest,
          });
          return { data: data.items, total: data.total, success: true };
        }}
        search={{ labelWidth: 'auto' }}
      />
    </PageContainer>
  );
}
