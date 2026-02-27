import { ModalForm, ProFormText, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { message } from 'antd';
import { createCustomer, updateCustomer } from '@/api/customers';
import { CurrencyTypeLabels, PaymentMethodLabels, TradeTermLabels } from '@/types/api';
import type { CustomerRead } from '@/types/models';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  record?: CustomerRead;
}

export default function CustomerForm({ open, onClose, onSuccess, record }: Props) {
  const isEdit = !!record;

  return (
    <ModalForm
      title={isEdit ? '编辑客户' : '新建客户'}
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      initialValues={record || {}}
      width={700}
      grid
      colProps={{ span: 12 }}
      onFinish={async (values: Record<string, unknown>) => {
        if (isEdit) {
          await updateCustomer(record!.id, values as never);
          message.success('更新成功');
        } else {
          await createCustomer(values as never);
          message.success('创建成功');
        }
        onSuccess();
        return true;
      }}
    >
      <ProFormText name="name" label="客户名称" rules={[{ required: true, max: 200 }]} />
      <ProFormText name="short_name" label="简称" />
      <ProFormText name="country" label="国家" rules={[{ required: true, max: 100 }]} />
      <ProFormText name="contact_person" label="联系人" rules={[{ required: true, max: 100 }]} />
      <ProFormText name="phone" label="电话" />
      <ProFormText name="email" label="邮箱" />
      <ProFormSelect name="currency" label="币种" valueEnum={CurrencyTypeLabels} rules={[{ required: true }]} />
      <ProFormSelect name="payment_method" label="付款方式" valueEnum={PaymentMethodLabels} rules={[{ required: true }]} />
      <ProFormText name="payment_terms" label="付款条件" />
      <ProFormSelect name="trade_term" label="贸易条款" valueEnum={TradeTermLabels} />
      <ProFormTextArea name="address" label="地址" colProps={{ span: 24 }} />
      <ProFormTextArea name="remark" label="备注" colProps={{ span: 24 }} />
    </ModalForm>
  );
}
