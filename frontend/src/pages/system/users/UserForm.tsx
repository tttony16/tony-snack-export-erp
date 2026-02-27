import { ModalForm, ProFormText, ProFormSelect } from '@ant-design/pro-components';
import { message } from 'antd';
import { createUser, updateUser } from '@/api/system';
import { UserRoleLabels } from '@/types/api';
import type { UserRead } from '@/types/models';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  record?: UserRead;
}

export default function UserForm({ open, onClose, onSuccess, record }: Props) {
  const isEdit = !!record;

  return (
    <ModalForm
      title={isEdit ? '编辑用户' : '新建用户'}
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      initialValues={record || { role: 'viewer' }}
      width={500}
      onFinish={async (values: Record<string, unknown>) => {
        if (isEdit) {
          await updateUser(record!.id, {
            display_name: values.display_name as string,
            email: values.email as string,
            phone: values.phone as string,
          });
          message.success('更新成功');
        } else {
          await createUser(values as never);
          message.success('创建成功');
        }
        onSuccess();
        return true;
      }}
    >
      <ProFormText
        name="username"
        label="用户名"
        rules={[{ required: true, min: 2, max: 50 }]}
        disabled={isEdit}
      />
      {!isEdit && (
        <ProFormText.Password
          name="password"
          label="密码"
          rules={[{ required: true, min: 6 }]}
        />
      )}
      <ProFormText name="display_name" label="显示名称" rules={[{ required: true, max: 100 }]} />
      <ProFormText name="email" label="邮箱" />
      <ProFormText name="phone" label="电话" />
      <ProFormSelect
        name="role"
        label="角色"
        valueEnum={UserRoleLabels}
        rules={[{ required: true }]}
        disabled={isEdit}
      />
    </ModalForm>
  );
}
