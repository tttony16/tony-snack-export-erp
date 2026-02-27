import { useState } from 'react';
import {
  ModalForm,
  ProFormSelect,
  ProFormDatePicker,
  ProFormText,
  ProFormTextArea,
} from '@ant-design/pro-components';
import { Table, InputNumber, Select, Input, message } from 'antd';
import { createReceivingNote } from '@/api/warehouse';
import { getPurchaseOrder } from '@/api/purchaseOrders';
import { listPurchaseOrders } from '@/api/purchaseOrders';
import { InspectionResultLabels } from '@/types/api';
import type { ReceivingNoteItemCreate } from '@/types/models';

interface Props {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function ReceivingNoteForm({ open, onClose, onSuccess }: Props) {
  const [noteItems, setNoteItems] = useState<ReceivingNoteItemCreate[]>([]);

  const handlePOSelect = async (poId: string) => {
    const po = await getPurchaseOrder(poId);
    setNoteItems(
      po.items.map((item) => ({
        purchase_order_item_id: item.id,
        product_id: item.product_id,
        expected_quantity: item.quantity - item.received_quantity,
        actual_quantity: item.quantity - item.received_quantity,
        inspection_result: 'passed' as const,
        failed_quantity: 0,
        production_date: '',
      })),
    );
  };

  const updateNoteItem = (index: number, field: string, value: unknown) => {
    const updated = [...noteItems];
    (updated[index] as unknown as Record<string, unknown>)[field] = value;
    setNoteItems(updated);
  };

  return (
    <ModalForm
      title="新建收货单"
      open={open}
      modalProps={{ onCancel: onClose, destroyOnClose: true }}
      width={900}
      onFinish={async (values: Record<string, unknown>) => {
        if (noteItems.length === 0) {
          message.warning('请先选择采购单');
          return false;
        }
        const hasEmptyDate = noteItems.some((i) => !i.production_date);
        if (hasEmptyDate) {
          message.warning('请填写所有明细的生产日期');
          return false;
        }
        await createReceivingNote({
          purchase_order_id: values.purchase_order_id as string,
          receiving_date: values.receiving_date as string,
          receiver: values.receiver as string,
          remark: values.remark as string,
          items: noteItems,
        });
        message.success('创建成功');
        onSuccess();
        return true;
      }}
    >
      <ProFormSelect
        name="purchase_order_id"
        label="采购单"
        rules={[{ required: true }]}
        showSearch
        request={async ({ keyWords }) => {
          const data = await listPurchaseOrders({ keyword: keyWords, page_size: 50, status: 'ordered' });
          return data.items.map((po) => ({ value: po.id, label: po.order_no }));
        }}
        fieldProps={{ onChange: handlePOSelect }}
      />
      <ProFormDatePicker name="receiving_date" label="收货日期" rules={[{ required: true }]} />
      <ProFormText name="receiver" label="验收人" rules={[{ required: true }]} />
      <ProFormTextArea name="remark" label="备注" />

      {noteItems.length > 0 && (
        <Table
          dataSource={noteItems}
          rowKey={(_, idx) => String(idx)}
          pagination={false}
          size="small"
          columns={[
            { title: '商品ID', dataIndex: 'product_id', ellipsis: true, width: 200 },
            { title: '应收', dataIndex: 'expected_quantity', width: 70 },
            {
              title: '实收',
              dataIndex: 'actual_quantity',
              width: 90,
              render: (_, __, idx) => (
                <InputNumber
                  min={0}
                  value={noteItems[idx].actual_quantity}
                  onChange={(v) => updateNoteItem(idx, 'actual_quantity', v || 0)}
                />
              ),
            },
            {
              title: '检验结果',
              dataIndex: 'inspection_result',
              width: 120,
              render: (_, __, idx) => (
                <Select
                  value={noteItems[idx].inspection_result}
                  onChange={(v) => updateNoteItem(idx, 'inspection_result', v)}
                  options={Object.entries(InspectionResultLabels).map(([v, l]) => ({ value: v, label: l }))}
                  size="small"
                  style={{ width: 110 }}
                />
              ),
            },
            {
              title: '不合格数',
              width: 90,
              render: (_, __, idx) => (
                <InputNumber
                  min={0}
                  value={noteItems[idx].failed_quantity}
                  onChange={(v) => updateNoteItem(idx, 'failed_quantity', v || 0)}
                  size="small"
                />
              ),
            },
            {
              title: '生产日期',
              width: 140,
              render: (_, __, idx) => (
                <Input
                  type="date"
                  value={noteItems[idx].production_date}
                  onChange={(e) => updateNoteItem(idx, 'production_date', e.target.value)}
                  size="small"
                />
              ),
            },
          ]}
        />
      )}
    </ModalForm>
  );
}
