import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '@ant-design/pro-components';
import {
  Descriptions,
  Table,
  Card,
  Space,
  Button,
  Steps,
  message,
  Spin,
  InputNumber,
  Select,
  Input,
  Popconfirm,
} from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import {
  getLogistics,
  updateLogisticsStatus,
  addLogisticsCost,
  deleteLogisticsCost,
} from '@/api/logistics';
import {
  LogisticsStatusLabels,
  LogisticsStatusColors,
  LogisticsCostTypeLabels,
  CurrencyTypeLabels,
} from '@/types/api';
import type { LogisticsStatus } from '@/types/api';
import type { LogisticsRecordRead } from '@/types/models';
import { formatDate, formatDateTime, formatCurrency, formatEnum } from '@/utils/format';
import StatusTag from '@/components/StatusTag';
import PermissionButton from '@/components/PermissionButton';

const STATUS_STEPS: LogisticsStatus[] = [
  'booked',
  'customs_cleared',
  'loaded_on_ship',
  'in_transit',
  'arrived',
  'picked_up',
  'delivered',
];

export default function LogisticsDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [record, setRecord] = useState<LogisticsRecordRead>();
  const [loading, setLoading] = useState(true);
  const [addingCost, setAddingCost] = useState(false);
  const [newCost, setNewCost] = useState({ cost_type: 'ocean_freight', amount: 0, currency: 'USD', remark: '' });

  const load = async () => {
    if (!id) return;
    setLoading(true);
    try {
      setRecord(await getLogistics(id));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading || !record) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  const currentStep = STATUS_STEPS.indexOf(record.status as LogisticsStatus);
  const nextStatus = currentStep < STATUS_STEPS.length - 1 ? STATUS_STEPS[currentStep + 1] : null;

  const handleAdvanceStatus = async () => {
    if (!nextStatus) return;
    await updateLogisticsStatus(record.id, nextStatus);
    message.success(`状态已更新为: ${LogisticsStatusLabels[nextStatus]}`);
    load();
  };

  const handleAddCost = async () => {
    await addLogisticsCost(record.id, newCost as never);
    message.success('费用添加成功');
    setAddingCost(false);
    setNewCost({ cost_type: 'ocean_freight', amount: 0, currency: 'USD', remark: '' });
    load();
  };

  const handleDeleteCost = async (costId: string) => {
    await deleteLogisticsCost(record.id, costId);
    message.success('费用已删除');
    load();
  };

  return (
    <PageContainer
      title={`物流记录 ${record.logistics_no}`}
      extra={
        <Space>
          {nextStatus && (
            <PermissionButton permission="logistics:edit" type="primary" onClick={handleAdvanceStatus}>
              推进到: {LogisticsStatusLabels[nextStatus]}
            </PermissionButton>
          )}
          <Button onClick={() => navigate('/logistics')}>返回列表</Button>
        </Space>
      }
    >
      <Card title="状态流转" style={{ marginBottom: 16 }}>
        <Steps
          current={currentStep}
          items={STATUS_STEPS.map((s) => ({
            title: LogisticsStatusLabels[s],
          }))}
        />
      </Card>

      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Descriptions column={3}>
          <Descriptions.Item label="物流编号">{record.logistics_no}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <StatusTag value={record.status} statusMap={LogisticsStatusLabels} colorMap={LogisticsStatusColors} />
          </Descriptions.Item>
          <Descriptions.Item label="船公司">{record.shipping_company || '-'}</Descriptions.Item>
          <Descriptions.Item label="船名航次">{record.vessel_voyage || '-'}</Descriptions.Item>
          <Descriptions.Item label="提单号">{record.bl_no || '-'}</Descriptions.Item>
          <Descriptions.Item label="报关单号">{record.customs_declaration_no || '-'}</Descriptions.Item>
          <Descriptions.Item label="装港">{record.port_of_loading}</Descriptions.Item>
          <Descriptions.Item label="卸港">{record.port_of_discharge}</Descriptions.Item>
          <Descriptions.Item label="ETD">{formatDate(record.etd)}</Descriptions.Item>
          <Descriptions.Item label="ETA">{formatDate(record.eta)}</Descriptions.Item>
          <Descriptions.Item label="实际离港">{formatDate(record.actual_departure_date)}</Descriptions.Item>
          <Descriptions.Item label="实际到港">{formatDate(record.actual_arrival_date)}</Descriptions.Item>
          <Descriptions.Item label="总费用">{formatCurrency(record.total_cost)}</Descriptions.Item>
          <Descriptions.Item label="备注">{record.remark || '-'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatDateTime(record.created_at)}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Card
        title="费用明细"
        extra={
          <PermissionButton
            permission="logistics:edit"
            type="link"
            icon={<PlusOutlined />}
            onClick={() => setAddingCost(true)}
          >
            添加费用
          </PermissionButton>
        }
      >
        <Table
          dataSource={record.costs}
          rowKey="id"
          pagination={false}
          columns={[
            {
              title: '费用类型',
              dataIndex: 'cost_type',
              render: (v) => formatEnum(v as string, LogisticsCostTypeLabels),
            },
            { title: '金额', dataIndex: 'amount', render: (v) => formatCurrency(v as number) },
            {
              title: '币种',
              dataIndex: 'currency',
              render: (v) => formatEnum(v as string, CurrencyTypeLabels),
            },
            { title: '备注', dataIndex: 'remark' },
            {
              title: '操作',
              width: 80,
              render: (_, cost) => (
                <Popconfirm title="确认删除?" onConfirm={() => handleDeleteCost(cost.id)}>
                  <a style={{ color: 'red' }}>删除</a>
                </Popconfirm>
              ),
            },
          ]}
          footer={() =>
            addingCost ? (
              <Space>
                <Select
                  value={newCost.cost_type}
                  onChange={(v) => setNewCost({ ...newCost, cost_type: v })}
                  options={Object.entries(LogisticsCostTypeLabels).map(([v, l]) => ({ value: v, label: l }))}
                  style={{ width: 120 }}
                />
                <InputNumber
                  placeholder="金额"
                  min={0}
                  precision={2}
                  value={newCost.amount}
                  onChange={(v) => setNewCost({ ...newCost, amount: v || 0 })}
                />
                <Select
                  value={newCost.currency}
                  onChange={(v) => setNewCost({ ...newCost, currency: v })}
                  options={Object.entries(CurrencyTypeLabels).map(([v, l]) => ({ value: v, label: l }))}
                  style={{ width: 140 }}
                />
                <Input
                  placeholder="备注"
                  value={newCost.remark}
                  onChange={(e) => setNewCost({ ...newCost, remark: e.target.value })}
                  style={{ width: 120 }}
                />
                <Button type="primary" size="small" onClick={handleAddCost}>添加</Button>
                <Button size="small" onClick={() => setAddingCost(false)}>取消</Button>
              </Space>
            ) : null
          }
        />
      </Card>
    </PageContainer>
  );
}
