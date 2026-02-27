import { useState, useEffect } from 'react';
import { Drawer, Table, Button, InputNumber, Space, message, Popconfirm } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { addSupplierProduct, removeSupplierProduct } from '@/api/suppliers';
import { listProducts } from '@/api/products';
import type { SupplierProductRead } from '@/types/models';
import request from '@/utils/request';
import EntitySelect from '@/components/EntitySelect';

interface Props {
  open: boolean;
  onClose: () => void;
  supplierId: string;
  supplierName: string;
}

export default function SupplierProducts({ open, onClose, supplierId, supplierName }: Props) {
  const [products, setProducts] = useState<(SupplierProductRead & { product_name?: string })[]>([]);
  const [loading, setLoading] = useState(false);
  const [addProductId, setAddProductId] = useState<string>();
  const [addPrice, setAddPrice] = useState<number>();

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data: SupplierProductRead[] = await request.get(`/suppliers/${supplierId}/products`);
      setProducts(Array.isArray(data) ? data : []);
    } catch {
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && supplierId) {
      loadProducts();
    }
  }, [open, supplierId]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleAdd = async () => {
    if (!addProductId) {
      message.warning('请选择商品');
      return;
    }
    await addSupplierProduct(supplierId, {
      product_id: addProductId,
      supply_price: addPrice,
    });
    message.success('添加成功');
    setAddProductId(undefined);
    setAddPrice(undefined);
    loadProducts();
  };

  const handleRemove = async (productId: string) => {
    await removeSupplierProduct(supplierId, productId);
    message.success('删除成功');
    loadProducts();
  };

  return (
    <Drawer
      title={`${supplierName} - 供应商品管理`}
      open={open}
      onClose={onClose}
      width={600}
      destroyOnClose
    >
      <Space style={{ marginBottom: 16 }}>
        <EntitySelect
          fetchFn={listProducts}
          labelField="name_cn"
          placeholder="搜索商品"
          style={{ width: 250 }}
          value={addProductId}
          onChange={(v) => setAddProductId(v as string)}
        />
        <InputNumber
          placeholder="供应价"
          min={0}
          precision={2}
          value={addPrice}
          onChange={(v) => setAddPrice(v ?? undefined)}
        />
        <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
          添加
        </Button>
      </Space>
      <Table
        dataSource={products}
        rowKey="id"
        loading={loading}
        pagination={false}
        columns={[
          { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
          { title: '供应价', dataIndex: 'supply_price', render: (v) => v ?? '-' },
          {
            title: '操作',
            render: (_, record) => (
              <Popconfirm title="确认删除?" onConfirm={() => handleRemove(record.product_id)}>
                <a style={{ color: 'red' }}>删除</a>
              </Popconfirm>
            ),
          },
        ]}
      />
    </Drawer>
  );
}
