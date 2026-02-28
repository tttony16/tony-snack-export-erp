import { useEffect, useState } from 'react';
import { getCategoryTree } from '@/api/productCategories';
import type { ProductCategoryTreeNode } from '@/types/models';

function flattenTree(
  nodes: ProductCategoryTreeNode[],
  map: Map<string, string>,
) {
  for (const node of nodes) {
    map.set(node.id, node.name);
    if (node.children.length > 0) {
      flattenTree(node.children, map);
    }
  }
}

export function useCategoryMap() {
  const [categoryMap, setCategoryMap] = useState<Map<string, string>>(new Map());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCategoryTree()
      .then((tree) => {
        const map = new Map<string, string>();
        flattenTree(tree, map);
        setCategoryMap(map);
      })
      .finally(() => setLoading(false));
  }, []);

  const getCategoryName = (id: string | undefined | null): string => {
    if (!id) return '-';
    return categoryMap.get(id) || id;
  };

  return { categoryMap, getCategoryName, loading };
}
