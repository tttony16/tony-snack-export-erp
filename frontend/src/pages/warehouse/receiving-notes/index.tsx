import { useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { PlusOutlined } from '@ant-design/icons';
import { listReceivingNotes } from '@/api/warehouse';
import type { ReceivingNoteListRead } from '@/types/models';
import { formatDate } from '@/utils/format';
import PermissionButton from '@/components/PermissionButton';
import ReceivingNoteForm from './ReceivingNoteForm';

export default function ReceivingNotesPage() {
  const actionRef = useRef<ActionType>();
  const [searchParams] = useSearchParams();
  const [formOpen, setFormOpen] = useState(false);

  const columns: ProColumns<ReceivingNoteListRead>[] = [
    { title: '收货单号', dataIndex: 'note_no', width: 140 },
    { title: '采购单ID', dataIndex: 'purchase_order_id', ellipsis: true, hideInSearch: true },
    {
      title: '收货日期',
      dataIndex: 'receiving_date',
      hideInSearch: true,
      width: 110,
      render: (_, r) => formatDate(r.receiving_date),
    },
    { title: '验收人', dataIndex: 'receiver', width: 100, hideInSearch: true },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      hideInSearch: true,
      width: 170,
      render: (_, r) => formatDate(r.created_at),
    },
  ];

  return (
    <PageContainer>
      <ProTable<ReceivingNoteListRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        params={{ keyword: searchParams.get('keyword') || undefined }}
        request={async (params) => {
          const { current, pageSize, keyword, ...rest } = params;
          const data = await listReceivingNotes({
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
            permission="warehouse:operate"
            onClick={() => setFormOpen(true)}
          >
            新建收货单
          </PermissionButton>,
        ]}
      />
      <ReceivingNoteForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
      />
    </PageContainer>
  );
}
