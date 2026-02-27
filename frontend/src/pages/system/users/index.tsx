import { useRef, useState } from 'react';
import { PageContainer, ProTable, type ActionType, type ProColumns } from '@ant-design/pro-components';
import { Switch, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { listUsers, updateUserStatus, updateUserRole } from '@/api/system';
import { UserRoleLabels } from '@/types/api';
import type { UserRead } from '@/types/models';
import { formatDateTime } from '@/utils/format';
import PermissionButton from '@/components/PermissionButton';
import EnumSelect from '@/components/EnumSelect';
import UserForm from './UserForm';

export default function SystemUsersPage() {
  const actionRef = useRef<ActionType>();
  const [formOpen, setFormOpen] = useState(false);
  const [editRecord, setEditRecord] = useState<UserRead | undefined>();

  const columns: ProColumns<UserRead>[] = [
    { title: '用户名', dataIndex: 'username', width: 120 },
    { title: '显示名称', dataIndex: 'display_name', width: 120, hideInSearch: true },
    {
      title: '角色',
      dataIndex: 'role',
      width: 120,
      valueEnum: UserRoleLabels,
      render: (_, record) => (
        <EnumSelect
          enumMap={UserRoleLabels}
          value={record.role}
          size="small"
          style={{ width: 120 }}
          onChange={async (value) => {
            await updateUserRole(record.id, value as string);
            message.success('角色更新成功');
            actionRef.current?.reload();
          }}
        />
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      width: 80,
      valueEnum: { true: '启用', false: '停用' },
      render: (_, record) => (
        <Switch
          checked={record.is_active}
          checkedChildren="启用"
          unCheckedChildren="停用"
          onChange={async (checked) => {
            await updateUserStatus(record.id, checked);
            message.success('状态更新成功');
            actionRef.current?.reload();
          }}
        />
      ),
    },
    { title: '邮箱', dataIndex: 'email', hideInSearch: true, ellipsis: true },
    {
      title: '最后登录',
      dataIndex: 'last_login_at',
      hideInSearch: true,
      width: 170,
      render: (_, r) => formatDateTime(r.last_login_at),
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
        <a key="edit" onClick={() => { setEditRecord(record); setFormOpen(true); }}>编辑</a>,
      ],
    },
  ];

  return (
    <PageContainer>
      <ProTable<UserRead>
        actionRef={actionRef}
        rowKey="id"
        columns={columns}
        request={async (params) => {
          const { current, pageSize, keyword, ...rest } = params;
          const data = await listUsers({
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
            permission="user:manage"
            onClick={() => { setEditRecord(undefined); setFormOpen(true); }}
          >
            新建用户
          </PermissionButton>,
        ]}
      />
      <UserForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSuccess={() => { setFormOpen(false); actionRef.current?.reload(); }}
        record={editRecord}
      />
    </PageContainer>
  );
}
