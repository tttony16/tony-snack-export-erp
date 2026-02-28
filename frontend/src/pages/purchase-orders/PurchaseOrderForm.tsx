import { useRef, useState } from 'react';
import {
  ModalForm,
  ProFormSelect,
  ProFormDatePicker,
  ProFormTextArea,
  EditableProTable,
  type ProFormInstance,
} from '@ant-design/pro-components';
import type { ProColumns } from '@ant-design/pro-components';
import { Button, message, Popover, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { createPurchaseOrder, updatePurchaseOrder } from '@/api/purchaseOrders';
import { listSuppliers } from '@/api/suppliers';
import { listSalesOrders } from '@/api/salesOrders';
import { listProducts } from '@/api/products';
import { UnitTypeLabels } from '@/types/api';
import type { PurchaseOrderRead, PurchaseOrderItemCreate } from '@/types/models';
import EntitySelect from '@/components/EntitySelect';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
  record?: PurchaseOrderRead;
}

type EditableItem = PurchaseOrderItemCreate & { id?: string };

export default function PurchaseOrderForm({ open, onClose, onSuccess, record }: Props) {
  const isEdit = !!record;
  const formRef = useRef<ProFormInstance>();
  const [editableKeys, setEditableKeys] = useState<React.Key[]>(
    () => record?.items?.map((i) => i.id) || [],
  );
  const [pickerOpen, setPickerOpen] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);

  const handleBatchAdd = () => {
    if (selectedProducts.length === 0) return;
    const currentItems: EditableItem[] = formRef.current?.getFieldValue('items') || [];
    const existingProductIds = new Set(currentItems.map((i) => i.product_id));
    const newItems: EditableItem[] = selectedProducts
      .filter((pid) => !existingProductIds.has(pid))
      .map((pid) => ({
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        product_id: pid,
        quantity: 1,
        unit: 'carton' as const,
        unit_price: 0,
      }));
    if (newItems.length === 0) {
      message.info('所选商品已在明细中');
      setSelectedProducts([]);
      setPickerOpen(false);
      return;
    }
    const allItems = [...currentItems, ...newItems];
    formRef.current?.setFieldsValue({ items: allItems });
    setEditableKeys(allItems.map((i) => i.id!));
    setSelectedProducts([]);
    setPickerOpen(false);
  };

  const itemColumns: ProColumns<EditableItem>[] = [
    {
      title: '商品',
      dataIndex: 'product_id',
      width: 220,
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
      editable: false,
      width: 120,
      render: (_, row) => ((row.quantity || 0) * (row.unit_price || 0)).toFixed(2),
    },
    { title: '操作', valueType: 'option', width: 60 },
  ];

  return (
    <ModalForm
      title={isEdit ? '编辑采购订单' : '新建采购订单'}
      open={open}
      formRef={formRef}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      initialValues={
        isEdit
          ? { ...record, items: record.items.map((i) => ({ ...i, id: i.id })) }
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
          items: items.map(({ product_id, quantity, unit, unit_price, sales_order_item_id }) => ({
            product_id,
            quantity,
            unit,
            unit_price,
            sales_order_item_id,
          })),
        };
        if (isEdit) {
          await updatePurchaseOrder(record!.id, payload as never);
          message.success('更新成功');
        } else {
          await createPurchaseOrder(payload as never);
          message.success('创建成功');
        }
        onSuccess();
        return true;
      }}
    >
      <ProFormSelect
        name="supplier_id"
        label="供应商"
        rules={[{ required: true }]}
        showSearch
        request={async ({ keyWords }) => {
          const data = await listSuppliers({ keyword: keyWords, page_size: 50 });
          return data.items.map((s) => ({ value: s.id, label: s.name }));
        }}
      />
      <ProFormDatePicker name="order_date" label="订单日期" rules={[{ required: true }]} />
      <ProFormDatePicker name="required_date" label="要求交期" />
      <ProFormSelect
        name="sales_order_ids"
        label="关联销售单"
        mode="multiple"
        showSearch
        request={async ({ keyWords }) => {
          const data = await listSalesOrders({ keyword: keyWords, page_size: 50 });
          return data.items.map((s) => ({ value: s.id, label: s.order_no }));
        }}
        colProps={{ span: 16 }}
      />
      <ProFormTextArea name="remark" label="备注" colProps={{ span: 24 }} />

      <EditableProTable<EditableItem>
        name="items"
        headerTitle={
          <Space>
            采购明细
            <Popover
              open={pickerOpen}
              onOpenChange={setPickerOpen}
              trigger="click"
              placement="bottomLeft"
              content={
                <div style={{ width: 320 }}>
                  <EntitySelect
                    mode="multiple"
                    fetchFn={listProducts}
                    labelField="name_cn"
                    placeholder="搜索并选择商品"
                    value={selectedProducts}
                    onChange={(val) => setSelectedProducts(val as string[])}
                    style={{ width: '100%', marginBottom: 8 }}
                  />
                  <Button type="primary" block onClick={handleBatchAdd}>
                    添加到明细
                  </Button>
                </div>
              }
            >
              <Button type="primary" size="small" icon={<PlusOutlined />}>
                添加商品
              </Button>
            </Popover>
          </Space>
        }
        columns={itemColumns}
        rowKey="id"
        recordCreatorProps={false}
        editable={{
          type: 'multiple',
          editableKeys,
          onChange: setEditableKeys,
          actionRender: (_row, _config, defaultDom) => [defaultDom.delete],
        }}
      />
    </ModalForm>
  );
}
