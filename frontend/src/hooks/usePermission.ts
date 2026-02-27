import { useCallback } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import type { UserRole } from '@/types/api';

const ROLE_PERMISSIONS: Record<UserRole, Set<string> | 'all'> = {
  super_admin: 'all',
  admin: new Set([
    'product:view', 'product:edit', 'product:import',
    'customer:view', 'customer:edit',
    'supplier:view', 'supplier:edit',
    'sales_order:view', 'sales_order:edit', 'sales_order:confirm',
    'purchase_order:view', 'purchase_order:edit', 'purchase_order:confirm',
    'warehouse:operate', 'inventory:view',
    'container:view', 'container:edit', 'container:confirm', 'container:stuffing', 'packing_list:export',
    'logistics:view', 'logistics:edit',
    'audit_log:view', 'statistics:view',
  ]),
  sales: new Set([
    'product:view',
    'customer:view', 'customer:edit',
    'sales_order:view', 'sales_order:edit',
    'purchase_order:view',
    'inventory:view',
    'container:view', 'container:edit', 'packing_list:export',
    'logistics:view', 'logistics:edit',
  ]),
  purchaser: new Set([
    'product:view',
    'supplier:view', 'supplier:edit',
    'sales_order:view',
    'purchase_order:view', 'purchase_order:edit',
    'inventory:view',
  ]),
  warehouse: new Set([
    'product:view',
    'sales_order:view',
    'inventory:view',
    'warehouse:operate',
    'container:view', 'container:stuffing', 'packing_list:export',
  ]),
  viewer: new Set([
    'product:view',
    'customer:view',
    'supplier:view',
    'sales_order:view',
    'purchase_order:view',
    'inventory:view',
    'container:view',
    'logistics:view',
  ]),
};

export function usePermission() {
  const user = useAuthStore((s) => s.user);

  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user) return false;
      const perms = ROLE_PERMISSIONS[user.role];
      if (perms === 'all') return true;
      return perms.has(permission);
    },
    [user],
  );

  return { hasPermission };
}
