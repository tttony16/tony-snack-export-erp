import { ModalForm, ProFormText, ProFormTextArea, ProFormSelect } from '@ant-design/pro-components';
import { message } from 'antd';
import { createSupplier, updateSupplier } from '@/api/suppliers';
import { ProductCategoryLabels } from '@/types/api';
import type { SupplierRead } from '@/types/models';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  record?: SupplierRead;
}

export default function SupplierForm({ open, onClose, onSuccess, record }: Props) {
  const isEdit = !!record;

  return (
    <ModalForm
      title={isEdit ? '编辑供应商' : '新建供应商'}
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      initialValues={record || {}}
      width={700}
      grid
      colProps={{ span: 12 }}
      onFinish={async (values: Record<string, unknown>) => {
        if (isEdit) {
          await updateSupplier(record!.id, values as never);
          message.success('更新成功');
        } else {
          await createSupplier(values as never);
          message.success('创建成功');
        }
        onSuccess();
        return true;
      }}
    >
      <ProFormText name="name" label="供应商名称" rules={[{ required: true, max: 200 }]} />
      <ProFormText name="contact_person" label="联系人" rules={[{ required: true, max: 100 }]} />
      <ProFormText name="phone" label="电话" rules={[{ required: true, max: 50 }]} />
      <ProFormText name="payment_terms" label="付款条件" />
      <ProFormSelect
        name="supply_categories"
        label="供应品类"
        mode="multiple"
        valueEnum={ProductCategoryLabels}
      />
      <ProFormSelect
        name="supply_brands"
        label="供应品牌"
        mode="tags"
        fieldProps={{ tokenSeparators: [','] }}
      />
      <ProFormText name="business_license" label="营业执照号" />
      <ProFormText name="food_production_license" label="食品生产许可证" />
      <ProFormTextArea name="address" label="地址" colProps={{ span: 24 }} />
      <ProFormTextArea name="remark" label="备注" colProps={{ span: 24 }} />
    </ModalForm>
  );
}
