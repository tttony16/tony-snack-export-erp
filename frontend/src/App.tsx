import { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import BasicLayout from '@/layouts/BasicLayout';
import AuthGuard from '@/layouts/AuthGuard';
import PageLoading from '@/components/PageLoading';

const Login = lazy(() => import('@/pages/login'));
const Dashboard = lazy(() => import('@/pages/dashboard'));
const Products = lazy(() => import('@/pages/products'));
const Customers = lazy(() => import('@/pages/customers'));
const Suppliers = lazy(() => import('@/pages/suppliers'));
const SalesOrders = lazy(() => import('@/pages/sales-orders'));
const SalesOrderDetail = lazy(() => import('@/pages/sales-orders/SalesOrderDetail'));
const PurchaseOrders = lazy(() => import('@/pages/purchase-orders'));
const PurchaseOrderDetail = lazy(() => import('@/pages/purchase-orders/PurchaseOrderDetail'));
const ReceivingNotes = lazy(() => import('@/pages/warehouse/receiving-notes'));
const Inventory = lazy(() => import('@/pages/warehouse/inventory'));
const Containers = lazy(() => import('@/pages/containers'));
const ContainerDetail = lazy(() => import('@/pages/containers/ContainerDetail'));
const Logistics = lazy(() => import('@/pages/logistics'));
const LogisticsDetail = lazy(() => import('@/pages/logistics/LogisticsDetail'));
const SystemUsers = lazy(() => import('@/pages/system/users'));
const AuditLogs = lazy(() => import('@/pages/system/audit-logs'));
const SystemConfigs = lazy(() => import('@/pages/system/configs'));
const Statistics = lazy(() => import('@/pages/statistics'));
const NotFound = lazy(() => import('@/components/NotFound'));

export default function App() {
  return (
    <Suspense fallback={<PageLoading />}>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <AuthGuard>
              <BasicLayout />
            </AuthGuard>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="products" element={<Products />} />
          <Route path="customers" element={<Customers />} />
          <Route path="suppliers" element={<Suppliers />} />
          <Route path="sales-orders" element={<SalesOrders />} />
          <Route path="sales-orders/:id" element={<SalesOrderDetail />} />
          <Route path="purchase-orders" element={<PurchaseOrders />} />
          <Route path="purchase-orders/:id" element={<PurchaseOrderDetail />} />
          <Route path="warehouse/receiving-notes" element={<ReceivingNotes />} />
          <Route path="warehouse/inventory" element={<Inventory />} />
          <Route path="containers" element={<Containers />} />
          <Route path="containers/:id" element={<ContainerDetail />} />
          <Route path="logistics" element={<Logistics />} />
          <Route path="logistics/:id" element={<LogisticsDetail />} />
          <Route path="system/users" element={<SystemUsers />} />
          <Route path="system/audit-logs" element={<AuditLogs />} />
          <Route path="system/configs" element={<SystemConfigs />} />
          <Route path="statistics" element={<Statistics />} />
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </Suspense>
  );
}
