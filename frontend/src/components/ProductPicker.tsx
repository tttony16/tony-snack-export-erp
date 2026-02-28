import { useState } from 'react';
import { Button, Popover, Select, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { listProducts, listBrands } from '@/api/products';
import CategoryCascader from './CategoryCascader';
import EntitySelect from './EntitySelect';

interface ProductPickerProps {
  onAdd: (productIds: string[]) => void;
}

export default function ProductPicker({ onAdd }: ProductPickerProps) {
  const [open, setOpen] = useState(false);
  const [categoryId, setCategoryId] = useState<string | undefined>();
  const [brand, setBrand] = useState<string | undefined>();
  const [selectedProducts, setSelectedProducts] = useState<string[]>([]);
  const [brandOptions, setBrandOptions] = useState<{ value: string; label: string }[]>([]);
  const [brandsLoaded, setBrandsLoaded] = useState(false);

  const loadBrands = async () => {
    if (brandsLoaded) return;
    const brands = await listBrands();
    setBrandOptions(brands.map((b) => ({ value: b, label: b })));
    setBrandsLoaded(true);
  };

  const handleAdd = () => {
    if (selectedProducts.length === 0) return;
    onAdd(selectedProducts);
    setSelectedProducts([]);
    setOpen(false);
  };

  const handleOpenChange = (visible: boolean) => {
    setOpen(visible);
    if (visible) loadBrands();
  };

  const extraParams: Record<string, unknown> = {};
  if (categoryId) extraParams.category_id = categoryId;
  if (brand) extraParams.brand = brand;

  return (
    <Popover
      open={open}
      onOpenChange={handleOpenChange}
      trigger="click"
      placement="bottomLeft"
      content={
        <div style={{ width: 360 }}>
          <Space style={{ width: '100%', marginBottom: 8 }} direction="vertical" size={8}>
            <Space style={{ width: '100%' }} size={8}>
              <CategoryCascader
                allowAnyLevel
                value={categoryId}
                onChange={(val) => {
                  setCategoryId(val);
                  setSelectedProducts([]);
                }}
                placeholder="按品类筛选"
                style={{ width: 170 }}
              />
              <Select
                allowClear
                showSearch
                placeholder="按品牌筛选"
                style={{ width: 170 }}
                options={brandOptions}
                value={brand}
                onChange={(val) => {
                  setBrand(val);
                  setSelectedProducts([]);
                }}
              />
            </Space>
            <EntitySelect
              mode="multiple"
              fetchFn={listProducts}
              labelField="name_cn"
              placeholder="搜索并选择商品"
              value={selectedProducts}
              onChange={(val) => setSelectedProducts(val as string[])}
              extraParams={extraParams}
              style={{ width: '100%' }}
            />
          </Space>
          <Button type="primary" block onClick={handleAdd} disabled={selectedProducts.length === 0}>
            添加到明细 {selectedProducts.length > 0 && `(${selectedProducts.length})`}
          </Button>
        </div>
      }
    >
      <Button type="primary" size="small" icon={<PlusOutlined />}>
        添加商品
      </Button>
    </Popover>
  );
}
