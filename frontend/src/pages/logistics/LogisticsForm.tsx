import { ModalForm, ProFormText, ProFormDatePicker, ProFormSelect, ProFormTextArea } from '@ant-design/pro-components';
import { message } from 'antd';
import { createLogistics, updateLogistics } from '@/api/logistics';
import { listContainerPlans } from '@/api/containers';
import type { LogisticsRecordRead } from '@/types/models';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  record?: LogisticsRecordRead;
}

export default function LogisticsForm({ open, onClose, onSuccess, record }: Props) {
  const isEdit = !!record;

  return (
    <ModalForm
      title={isEdit ? '编辑物流记录' : '新建物流记录'}
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      initialValues={record || {}}
      width={700}
      grid
      colProps={{ span: 12 }}
      onFinish={async (values: Record<string, unknown>) => {
        if (isEdit) {
          await updateLogistics(record!.id, values as never);
          message.success('更新成功');
        } else {
          await createLogistics(values as never);
          message.success('创建成功');
        }
        onSuccess();
        return true;
      }}
    >
      {!isEdit && (
        <ProFormSelect
          name="container_plan_id"
          label="排柜计划"
          rules={[{ required: true }]}
          showSearch
          request={async ({ keyWords }) => {
            const data = await listContainerPlans({ keyword: keyWords, page_size: 50 });
            return data.items.map((c) => ({ value: c.id, label: c.plan_no }));
          }}
        />
      )}
      <ProFormText name="shipping_company" label="船公司" />
      <ProFormText name="vessel_voyage" label="船名航次" />
      <ProFormText name="bl_no" label="提单号" />
      <ProFormText name="port_of_loading" label="装港" rules={[{ required: !isEdit }]} />
      <ProFormText name="port_of_discharge" label="卸港" />
      <ProFormDatePicker name="etd" label="预计离港" />
      <ProFormDatePicker name="eta" label="预计到港" />
      <ProFormDatePicker name="actual_departure_date" label="实际离港" />
      <ProFormDatePicker name="actual_arrival_date" label="实际到港" />
      <ProFormText name="customs_declaration_no" label="报关单号" />
      <ProFormTextArea name="remark" label="备注" colProps={{ span: 24 }} />
    </ModalForm>
  );
}
