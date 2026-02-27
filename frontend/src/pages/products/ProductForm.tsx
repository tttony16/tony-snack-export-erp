import { ModalForm, ProFormText, ProFormDigit, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { message } from 'antd';
import { createProduct, updateProduct } from '@/api/products';
import { ProductCategoryLabels } from '@/types/api';
import type { ProductRead } from '@/types/models';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  record?: ProductRead;
}

export default function ProductForm({ open, onClose, onSuccess, record }: Props) {
  const isEdit = !!record;

  return (
    <ModalForm
      title={isEdit ? '编辑商品' : '新建商品'}
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      initialValues={record || {}}
      width={800}
      grid
      colProps={{ span: 12 }}
      onFinish={async (values: Record<string, unknown>) => {
        if (isEdit) {
          await updateProduct(record!.id, values as never);
          message.success('更新成功');
        } else {
          await createProduct(values as never);
          message.success('创建成功');
        }
        onSuccess();
        return true;
      }}
    >
      <ProFormText
        name="sku_code"
        label="SKU 编码"
        rules={[{ required: true, max: 50 }]}
        disabled={isEdit}
      />
      <ProFormText name="name_cn" label="中文名称" rules={[{ required: true, max: 200 }]} />
      <ProFormText name="name_en" label="英文名称" rules={[{ required: true, max: 200 }]} />
      <ProFormSelect
        name="category"
        label="分类"
        valueEnum={ProductCategoryLabels}
        rules={[{ required: true }]}
      />
      <ProFormText name="brand" label="品牌" />
      <ProFormText name="barcode" label="条码" />
      <ProFormText name="spec" label="规格" rules={[{ required: true, max: 200 }]} />
      <ProFormText name="packing_spec" label="装箱规格" rules={[{ required: true, max: 200 }]} />
      <ProFormDigit name="unit_weight_kg" label="单位重量(kg)" rules={[{ required: true }]} min={0.001} fieldProps={{ precision: 3 }} />
      <ProFormDigit name="unit_volume_cbm" label="单位体积(cbm)" rules={[{ required: true }]} min={0.000001} fieldProps={{ precision: 6 }} />
      <ProFormDigit name="carton_length_cm" label="箱长(cm)" rules={[{ required: true }]} min={0.1} />
      <ProFormDigit name="carton_width_cm" label="箱宽(cm)" rules={[{ required: true }]} min={0.1} />
      <ProFormDigit name="carton_height_cm" label="箱高(cm)" rules={[{ required: true }]} min={0.1} />
      <ProFormDigit name="carton_gross_weight_kg" label="箱毛重(kg)" rules={[{ required: true }]} min={0.001} />
      <ProFormDigit name="shelf_life_days" label="保质期(天)" rules={[{ required: true }]} min={1} fieldProps={{ precision: 0 }} />
      <ProFormDigit name="default_purchase_price" label="默认采购价" min={0} fieldProps={{ precision: 2 }} />
      <ProFormText name="hs_code" label="HS编码" />
      <ProFormText name="image_url" label="图片URL" />
      <ProFormTextArea name="remark" label="备注" colProps={{ span: 24 }} />
    </ModalForm>
  );
}
