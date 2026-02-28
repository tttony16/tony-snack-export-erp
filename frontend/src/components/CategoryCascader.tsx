import { useEffect, useMemo, useState } from 'react';
import { Cascader } from 'antd';
import type { DefaultOptionType } from 'antd/es/cascader';
import { getCategoryTree } from '@/api/productCategories';
import type { ProductCategoryTreeNode } from '@/types/models';

interface CategoryCascaderProps {
  value?: string;
  onChange?: (value: string | undefined) => void;
  allowAnyLevel?: boolean;
  placeholder?: string;
  allowClear?: boolean;
  style?: React.CSSProperties;
  disabled?: boolean;
}

function treeToOptions(nodes: ProductCategoryTreeNode[]): DefaultOptionType[] {
  return nodes.map((node) => ({
    value: node.id,
    label: node.name,
    children: node.children.length > 0 ? treeToOptions(node.children) : undefined,
  }));
}

function buildIdToPathMap(
  nodes: ProductCategoryTreeNode[],
  path: string[] = [],
): Map<string, string[]> {
  const map = new Map<string, string[]>();
  for (const node of nodes) {
    const currentPath = [...path, node.id];
    map.set(node.id, currentPath);
    if (node.children.length > 0) {
      const childMap = buildIdToPathMap(node.children, currentPath);
      childMap.forEach((v, k) => map.set(k, v));
    }
  }
  return map;
}

export default function CategoryCascader({
  value,
  onChange,
  allowAnyLevel = false,
  placeholder = '请选择品类',
  allowClear = true,
  style,
  disabled,
}: CategoryCascaderProps) {
  const [tree, setTree] = useState<ProductCategoryTreeNode[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    getCategoryTree()
      .then(setTree)
      .finally(() => setLoading(false));
  }, []);

  const options = useMemo(() => treeToOptions(tree), [tree]);
  const idToPath = useMemo(() => buildIdToPathMap(tree), [tree]);

  // Convert the single ID value to a path array for Cascader
  const cascaderValue = value ? idToPath.get(value) : undefined;

  const handleChange = (selectedPath: (string | number)[] | null) => {
    if (!selectedPath || selectedPath.length === 0) {
      onChange?.(undefined);
    } else {
      // The last element in the path is the selected category ID
      onChange?.(selectedPath[selectedPath.length - 1] as string);
    }
  };

  return (
    <Cascader
      options={options}
      value={cascaderValue}
      onChange={handleChange as never}
      changeOnSelect={allowAnyLevel}
      placeholder={placeholder}
      allowClear={allowClear}
      loading={loading}
      style={style}
      disabled={disabled}
      showSearch={{
        filter: (inputValue, path) =>
          path.some((option) =>
            (option.label as string).toLowerCase().includes(inputValue.toLowerCase()),
          ),
      }}
    />
  );
}
