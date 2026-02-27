import { useMemo } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { ProLayout, type MenuDataItem } from '@ant-design/pro-components';
import {
  DashboardOutlined,
  ShoppingOutlined,
  TeamOutlined,
  ShopOutlined,
  FileTextOutlined,
  ShoppingCartOutlined,
  InboxOutlined,
  ContainerOutlined,
  SendOutlined,
  BarChartOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import { Dropdown, type MenuProps } from 'antd';
import { useAuthStore } from '@/store/useAuthStore';
import { logout as logoutApi } from '@/api/auth';
import { usePermission } from '@/hooks/usePermission';
import GlobalSearch from '@/components/GlobalSearch';

const allMenus: (MenuDataItem & { permission?: string })[] = [
  { path: '/dashboard', name: '工作台', icon: <DashboardOutlined /> },
  { path: '/products', name: '商品管理', icon: <ShoppingOutlined />, permission: 'product:view' },
  { path: '/customers', name: '客户管理', icon: <TeamOutlined />, permission: 'customer:view' },
  { path: '/suppliers', name: '供应商管理', icon: <ShopOutlined />, permission: 'supplier:view' },
  { path: '/sales-orders', name: '销售订单', icon: <FileTextOutlined />, permission: 'sales_order:view' },
  { path: '/purchase-orders', name: '采购订单', icon: <ShoppingCartOutlined />, permission: 'purchase_order:view' },
  {
    path: '/warehouse',
    name: '仓储管理',
    icon: <InboxOutlined />,
    permission: 'inventory:view',
    children: [
      { path: '/warehouse/receiving-notes', name: '收货单' },
      { path: '/warehouse/inventory', name: '库存查询' },
    ],
  },
  { path: '/containers', name: '排柜管理', icon: <ContainerOutlined />, permission: 'container:view' },
  { path: '/logistics', name: '物流管理', icon: <SendOutlined />, permission: 'logistics:view' },
  { path: '/statistics', name: '统计报表', icon: <BarChartOutlined />, permission: 'statistics:view' },
  {
    path: '/system',
    name: '系统管理',
    icon: <SettingOutlined />,
    permission: 'user:manage',
    children: [
      { path: '/system/users', name: '用户管理' },
      { path: '/system/audit-logs', name: '审计日志' },
      { path: '/system/configs', name: '系统配置' },
    ],
  },
];

export default function BasicLayout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, clearAuth } = useAuthStore();
  const { hasPermission } = usePermission();

  const filteredMenus = useMemo(() => {
    return allMenus.filter((menu) => {
      if (!menu.permission) return true;
      return hasPermission(menu.permission);
    });
  }, [hasPermission]);

  const handleLogout = async () => {
    try {
      await logoutApi();
    } finally {
      clearAuth();
      navigate('/login');
    }
  };

  const userMenuItems: MenuProps['items'] = [
    { key: 'logout', label: '退出登录' },
  ];

  return (
    <ProLayout
      title="零食出口 ERP"
      logo={false}
      layout="mix"
      fixSiderbar
      fixedHeader
      route={{ routes: filteredMenus }}
      location={{ pathname: location.pathname }}
      menuItemRender={(item, dom) => (
        <a onClick={() => item.path && navigate(item.path)}>{dom}</a>
      )}
      actionsRender={() => [
        <GlobalSearch key="search" />,
        <Dropdown
          key="user"
          menu={{
            items: userMenuItems,
            onClick: ({ key }) => {
              if (key === 'logout') handleLogout();
            },
          }}
        >
          <span style={{ cursor: 'pointer' }}>
            {user?.display_name || user?.username || '用户'}
          </span>
        </Dropdown>,
      ]}
    >
      <Outlet />
    </ProLayout>
  );
}
