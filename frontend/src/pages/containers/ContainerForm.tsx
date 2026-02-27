import { ModalForm, ProFormSelect, ProFormDigit, ProFormText, ProFormTextArea } from '@ant-design/pro-components';
import { message } from 'antd';
import { createContainerPlan } from '@/api/containers';
import { listSalesOrders } from '@/api/salesOrders';
import { ContainerTypeLabels } from '@/types/api';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ContainerForm({ open, onClose, onSuccess }: Props) {
  return (
    <ModalForm
      title="新建排柜计划"
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      width={600}
      onFinish={async (values: Record<string, unknown>) => {
        await createContainerPlan(values as never);
        message.success('创建成功');
        onSuccess();
        return true;
      }}
    >
      <ProFormSelect
        name="sales_order_ids"
        label="关联销售单"
        mode="multiple"
        rules={[{ required: true }]}
        showSearch
        request={async ({ keyWords }) => {
          const data = await listSalesOrders({ keyword: keyWords, page_size: 50 });
          return data.items.map((s) => ({ value: s.id, label: s.order_no }));
        }}
      />
      <ProFormSelect
        name="container_type"
        label="柜型"
        valueEnum={ContainerTypeLabels}
        rules={[{ required: true }]}
      />
      <ProFormDigit name="container_count" label="柜数" min={1} initialValue={1} rules={[{ required: true }]} />
      <ProFormText name="destination_port" label="目的港" />
      <ProFormTextArea name="remark" label="备注" />
    </ModalForm>
  );
}
