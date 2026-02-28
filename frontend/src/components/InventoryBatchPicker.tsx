import { useState, useEffect } from 'react';
import { Modal, Table, InputNumber, Input, Space, message, Tag } from 'antd';
import { listInventoryBatches } from '@/api/warehouse';
import type { InventoryBatchRead } from '@/types/models';
import { formatDate } from '@/utils/format';

export interface BatchPickerResult {
  inventory_record_id: string;
  product_id: string;
  sales_order_id: string | null;
  quantity: number;
  batch_no: string;
  production_date: string;
  product_name: string | null;
}

interface Props {
  open: boolean;
  onClose: () => void;
  onSelect: (result: BatchPickerResult) => void;
}

export default function InventoryBatchPicker({ open, onClose, onSelect }: Props) {
  const [batches, setBatches] = useState<InventoryBatchRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [keyword, setKeyword] = useState('');
  const [quantities, setQuantities] = useState<Record<string, number>>({});

  const load = async (search?: string) => {
    setLoading(true);
    try {
      const data = await listInventoryBatches({
        page_size: 100,
      });
      let filtered = data;
      if (search) {
        const lower = search.toLowerCase();
        filtered = data.filter(
          (b) =>
            b.product_name?.toLowerCase().includes(lower) ||
            b.batch_no.toLowerCase().includes(lower) ||
            b.sales_order_no?.toLowerCase().includes(lower)
        );
      }
      setBatches(filtered);
    } catch {
      setBatches([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      load();
      setQuantities({});
      setKeyword('');
    }
  }, [open]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSearch = () => {
    load(keyword);
  };

  const handleSelect = (record: InventoryBatchRead) => {
    const qty = quantities[record.id] || 0;
    if (qty <= 0) {
      message.warning('请输入分配数量');
      return;
    }
    if (qty > record.available_quantity) {
      message.error(`分配数量不能超过可用数量 ${record.available_quantity}`);
      return;
    }
    onSelect({
      inventory_record_id: record.id,
      product_id: record.product_id,
      sales_order_id: record.sales_order_id,
      quantity: qty,
      batch_no: record.batch_no,
      production_date: record.production_date,
      product_name: record.product_name,
    });
  };

  return (
    <Modal
      title="选择库存批次"
      open={open}
      onCancel={onClose}
      footer={null}
      width={1000}
      destroyOnClose
    >
      <Space style={{ marginBottom: 16 }}>
        <Input.Search
          placeholder="搜索商品名/批次号/订单号"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onSearch={handleSearch}
          style={{ width: 300 }}
          allowClear
        />
      </Space>
      <Table<InventoryBatchRead>
        dataSource={batches}
        rowKey="id"
        loading={loading}
        pagination={false}
        size="small"
        scroll={{ y: 400 }}
        columns={[
          { title: '商品名称', dataIndex: 'product_name', width: 150, ellipsis: true },
          { title: '关联订单', dataIndex: 'sales_order_no', width: 130 },
          { title: '批次号', dataIndex: 'batch_no', width: 130 },
          {
            title: '生产日期',
            dataIndex: 'production_date',
            width: 110,
            render: (v) => formatDate(v as string),
          },
          { title: '可用数量', dataIndex: 'available_quantity', width: 90 },
          {
            title: '保质期剩余',
            dataIndex: 'shelf_life_remaining_days',
            width: 100,
            render: (v: number | null) =>
              v !== null ? (
                <Tag color={v < 90 ? 'red' : v < 180 ? 'orange' : 'green'}>{v}天</Tag>
              ) : (
                '-'
              ),
          },
          {
            title: '分配数量',
            width: 120,
            render: (_, record) => (
              <InputNumber
                min={1}
                max={record.available_quantity}
                value={quantities[record.id]}
                onChange={(v) =>
                  setQuantities((prev) => ({ ...prev, [record.id]: v || 0 }))
                }
                size="small"
                style={{ width: 100 }}
              />
            ),
          },
          {
            title: '操作',
            width: 80,
            render: (_, record) => (
              <a onClick={() => handleSelect(record)}>选择</a>
            ),
          },
        ]}
      />
    </Modal>
  );
}
