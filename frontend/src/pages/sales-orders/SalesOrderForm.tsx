import { useRef } from 'react';
import {
  ModalForm,
  ProFormText,
  ProFormSelect,
  ProFormDatePicker,
  ProFormTextArea,
  EditableProTable,
  type EditableFormInstance,
} from '@ant-design/pro-components';
import type { ProColumns } from '@ant-design/pro-components';
import { message } from 'antd';
import { createSalesOrder, updateSalesOrder } from '@/api/salesOrders';
import { listCustomers } from '@/api/customers';
import { listProducts } from '@/api/products';
import {
  CurrencyTypeLabels,
  PaymentMethodLabels,
  TradeTermLabels,
  UnitTypeLabels,
} from '@/types/api';
import type { SalesOrderRead, SalesOrderItemCreate } from '@/types/models';
import EntitySelect from '@/components/EntitySelect';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  record?: SalesOrderRead;
}

type EditableItem = SalesOrderItemCreate & { id?: string };

export default function SalesOrderForm({ open, onClose, onSuccess, record }: Props) {
  const isEdit = !!record;
  const editableFormRef = useRef<EditableFormInstance>();

  const itemColumns: ProColumns<EditableItem>[] = [
    {
      title: '商品',
      dataIndex: 'product_id',
      renderFormItem: () => (
        <EntitySelect fetchFn={listProducts} labelField="name_cn" placeholder="搜索商品" />
      ),
    },
    { title: '数量', dataIndex: 'quantity', valueType: 'digit', width: 100 },
    {
      title: '单位',
      dataIndex: 'unit',
      valueType: 'select',
      width: 80,
      fieldProps: { options: Object.entries(UnitTypeLabels).map(([v, l]) => ({ value: v, label: l })) },
    },
    { title: '单价', dataIndex: 'unit_price', valueType: 'money', width: 120 },
    {
      title: '金额',
      dataIndex: 'amount',
      editable: false,
      width: 120,
      render: (_, row) => ((row.quantity || 0) * (row.unit_price || 0)).toFixed(2),
    },
    { title: '操作', valueType: 'option', width: 60 },
  ];

  return (
    <ModalForm
      title={isEdit ? '编辑销售订单' : '新建销售订单'}
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      initialValues={
        isEdit
          ? {
              ...record,
              items: record.items.map((item) => ({
                ...item,
                id: item.id,
              })),
            }
          : { items: [] }
      }
      width={900}
      grid
      colProps={{ span: 8 }}
      onFinish={async (values: Record<string, unknown>) => {
        const items = (values.items as EditableItem[]) || [];
        if (items.length === 0) {
          message.warning('请添加至少一个明细行');
          return false;
        }
        const payload = {
          ...values,
          items: items.map(({ product_id, quantity, unit, unit_price }) => ({
            product_id,
            quantity,
            unit,
            unit_price,
          })),
        };
        if (isEdit) {
          await updateSalesOrder(record!.id, payload as never);
          message.success('更新成功');
        } else {
          await createSalesOrder(payload as never);
          message.success('创建成功');
        }
        onSuccess();
        return true;
      }}
    >
      <ProFormSelect
        name="customer_id"
        label="客户"
        rules={[{ required: true }]}
        showSearch
        request={async ({ keyWords }) => {
          const data = await listCustomers({ keyword: keyWords, page_size: 50 });
          return data.items.map((c) => ({ value: c.id, label: c.name }));
        }}
      />
      <ProFormDatePicker name="order_date" label="订单日期" rules={[{ required: true }]} />
      <ProFormDatePicker name="required_delivery_date" label="要求交期" />
      <ProFormText name="destination_port" label="目的港" rules={[{ required: true }]} />
      <ProFormSelect name="trade_term" label="贸易条款" valueEnum={TradeTermLabels} rules={[{ required: true }]} />
      <ProFormSelect name="currency" label="币种" valueEnum={CurrencyTypeLabels} rules={[{ required: true }]} />
      <ProFormSelect name="payment_method" label="付款方式" valueEnum={PaymentMethodLabels} rules={[{ required: true }]} />
      <ProFormText name="payment_terms" label="付款条件" />
      <ProFormTextArea name="remark" label="备注" colProps={{ span: 24 }} />

      <EditableProTable<EditableItem>
        name="items"
        headerTitle="订单明细"
        columns={itemColumns}
        rowKey="id"
        editableFormRef={editableFormRef}
        recordCreatorProps={{
          newRecordType: 'dataSource',
          record: () => ({
            id: String(Date.now()),
            product_id: '',
            quantity: 1,
            unit: 'carton' as const,
            unit_price: 0,
          }),
        }}
        editable={{
          type: 'multiple',
          editableKeys: [],
          actionRender: (_row, _config, defaultDom) => [defaultDom.save, defaultDom.delete],
        }}
      />
    </ModalForm>
  );
}
