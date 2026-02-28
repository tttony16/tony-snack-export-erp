import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { PageContainer } from '@ant-design/pro-components';
import { Descriptions, Table, Card, Space, Button, Row, Col, message, Spin, Alert, Image, Modal, Input } from 'antd';
import { DownloadOutlined, PlusOutlined } from '@ant-design/icons';
import {
  getContainerPlan,
  getContainerSummary,
  recommendContainerType,
  validateContainer,
  confirmContainerPlan,
  cancelContainerPlan,
  uploadStuffingPhoto,
  addContainerItem,
} from '@/api/containers';
import { createOutboundOrder } from '@/api/outbound';
import {
  ContainerPlanStatusLabels,
  ContainerPlanStatusColors,
  ContainerTypeLabels,
} from '@/types/api';
import type { ContainerPlanRead, ContainerSummaryItem } from '@/types/models';
import { formatDate, formatDateTime, formatDecimal } from '@/utils/format';
import { downloadFile } from '@/utils/download';
import StatusTag from '@/components/StatusTag';
import PermissionButton from '@/components/PermissionButton';
import ContainerSummaryCard from './ContainerSummaryCard';
import InventoryBatchPicker, { type BatchPickerResult } from '@/components/InventoryBatchPicker';

export default function ContainerDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [plan, setPlan] = useState<ContainerPlanRead>();
  const [summaryItems, setSummaryItems] = useState<ContainerSummaryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [validationErrors, setValidationErrors] = useState<string[]>([]);
  const [photoModalOpen, setPhotoModalOpen] = useState(false);
  const [photoRecordId, setPhotoRecordId] = useState<string>('');
  const [photoUrl, setPhotoUrl] = useState('');
  const [photoDesc, setPhotoDesc] = useState('');
  const [batchPickerOpen, setBatchPickerOpen] = useState(false);

  const load = async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [planData, summaryData] = await Promise.all([
        getContainerPlan(id),
        getContainerSummary(id).catch(() => ({ items: [] })),
      ]);
      setPlan(planData);
      setSummaryItems(summaryData.items);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  if (loading || !plan) return <Spin style={{ display: 'block', margin: '100px auto' }} />;

  const handleValidate = async () => {
    const result = await validateContainer(plan.id);
    if (result.is_valid) {
      message.success('校验通过');
      setValidationErrors([]);
    } else {
      setValidationErrors(result.errors.map((e) => JSON.stringify(e)));
    }
  };

  const handleConfirm = async () => {
    await confirmContainerPlan(plan.id);
    message.success('确认成功');
    load();
  };

  const handleCancel = async () => {
    Modal.confirm({
      title: '取消排柜计划',
      content: '取消后将释放已预留的库存，确认取消？',
      onOk: async () => {
        await cancelContainerPlan(plan.id);
        message.success('已取消');
        load();
      },
    });
  };

  const handleCreateOutbound = async () => {
    Modal.confirm({
      title: '创建出库单',
      content: '将根据当前排柜计划创建出库单草稿，确认继续？',
      onOk: async () => {
        const order = await createOutboundOrder({ container_plan_id: plan.id });
        message.success(`出库单 ${order.order_no} 创建成功`);
        navigate(`/outbound/${order.id}`);
      },
    });
  };

  const handleRecommend = async () => {
    const result = await recommendContainerType(plan.id);
    const recs = result.recommendations
      .map((r) => `${r.container_type} x${r.count} (体积 ${formatDecimal(Number(r.volume_utilization))}%, 重量 ${formatDecimal(Number(r.weight_utilization))}%)`)
      .join('\n');
    message.info({
      content: `推荐方案:\n${recs}\n\n总体积: ${formatDecimal(Number(result.total_volume_cbm))} cbm\n总重量: ${formatDecimal(Number(result.total_weight_kg))} kg`,
      duration: 8,
    });
  };

  const handleExportPackingList = async () => {
    await downloadFile(`/containers/${plan.id}/packing-list`, `装箱单_${plan.plan_no}.xlsx`);
    message.success('导出成功');
  };

  const handleAddPhoto = async () => {
    if (!photoUrl) {
      message.warning('请输入照片URL');
      return;
    }
    await uploadStuffingPhoto(photoRecordId, { photo_url: photoUrl, description: photoDesc || undefined });
    message.success('照片添加成功');
    setPhotoModalOpen(false);
    setPhotoUrl('');
    setPhotoDesc('');
    load();
  };

  const handleBatchSelect = async (result: BatchPickerResult) => {
    if (!id) return;
    await addContainerItem(id, {
      container_seq: 1,
      inventory_record_id: result.inventory_record_id,
      quantity: result.quantity,
      volume_cbm: 0,
      weight_kg: 0,
    });
    message.success('配载添加成功');
    setBatchPickerOpen(false);
    load();
  };

  return (
    <PageContainer
      title={`排柜计划 ${plan.plan_no}`}
      extra={
        <Space>
          {plan.status === 'planning' && (
            <>
              <Button onClick={handleRecommend}>推荐柜型</Button>
              <Button onClick={handleValidate}>校验</Button>
              <PermissionButton permission="container:confirm" type="primary" onClick={handleConfirm}>
                确认
              </PermissionButton>
            </>
          )}
          {plan.status === 'confirmed' && (
            <PermissionButton permission="container:confirm" danger onClick={handleCancel}>
              取消计划
            </PermissionButton>
          )}
          {plan.status === 'loaded' && (
            <PermissionButton permission="outbound:edit" type="primary" onClick={handleCreateOutbound}>
              创建出库单
            </PermissionButton>
          )}
          {plan.status !== 'planning' && (
            <PermissionButton
              permission="packing_list:export"
              icon={<DownloadOutlined />}
              onClick={handleExportPackingList}
            >
              导出装箱单
            </PermissionButton>
          )}
          <Button onClick={() => navigate('/containers')}>返回列表</Button>
        </Space>
      }
    >
      {validationErrors.length > 0 && (
        <Alert
          type="error"
          message="校验未通过"
          description={validationErrors.join('; ')}
          closable
          onClose={() => setValidationErrors([])}
          style={{ marginBottom: 16 }}
        />
      )}

      <Card title="计划信息" style={{ marginBottom: 16 }}>
        <Descriptions column={3}>
          <Descriptions.Item label="计划号">{plan.plan_no}</Descriptions.Item>
          <Descriptions.Item label="状态">
            <StatusTag value={plan.status} statusMap={ContainerPlanStatusLabels} colorMap={ContainerPlanStatusColors} />
          </Descriptions.Item>
          <Descriptions.Item label="柜型">{ContainerTypeLabels[plan.container_type] || plan.container_type}</Descriptions.Item>
          <Descriptions.Item label="柜数">{plan.container_count}</Descriptions.Item>
          <Descriptions.Item label="目的港">{plan.destination_port}</Descriptions.Item>
          <Descriptions.Item label="备注">{plan.remark || '-'}</Descriptions.Item>
          <Descriptions.Item label="创建时间">{formatDateTime(plan.created_at)}</Descriptions.Item>
        </Descriptions>
      </Card>

      <Row gutter={16} style={{ marginBottom: 16 }}>
        {summaryItems.map((item) => (
          <Col key={item.container_seq} xs={24} sm={12} md={8} lg={6}>
            <ContainerSummaryCard item={item} />
          </Col>
        ))}
      </Row>

      <Card
        title="装柜明细"
        style={{ marginBottom: 16 }}
        extra={
          plan.status === 'planning' && (
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={() => setBatchPickerOpen(true)}
            >
              添加配载
            </Button>
          )
        }
      >
        <Table
          dataSource={plan.items}
          rowKey="id"
          pagination={false}
          columns={[
            { title: '柜序号', dataIndex: 'container_seq', width: 80 },
            { title: '商品ID', dataIndex: 'product_id', ellipsis: true },
            { title: '批次号', dataIndex: 'batch_no', width: 130 },
            { title: '生产日期', dataIndex: 'production_date', width: 110, render: (v) => v ? formatDate(v as string) : '-' },
            { title: '销售单ID', dataIndex: 'sales_order_id', ellipsis: true, render: (v) => v || '-' },
            { title: '数量', dataIndex: 'quantity', width: 80 },
            { title: '体积(cbm)', dataIndex: 'volume_cbm', width: 100, render: (v) => formatDecimal(v as number) },
            { title: '重量(kg)', dataIndex: 'weight_kg', width: 100, render: (v) => formatDecimal(v as number) },
          ]}
        />
      </Card>

      {plan.stuffing_records.length > 0 && (
        <Card title="装柜记录">
          <Table
            dataSource={plan.stuffing_records}
            rowKey="id"
            pagination={false}
            columns={[
              { title: '柜序号', dataIndex: 'container_seq', width: 80 },
              { title: '柜号', dataIndex: 'container_no', width: 140 },
              { title: '铅封号', dataIndex: 'seal_no', width: 120 },
              { title: '装柜日期', dataIndex: 'stuffing_date', width: 110, render: (v) => formatDate(v as string) },
              { title: '装柜地点', dataIndex: 'stuffing_location' },
              {
                title: '照片',
                dataIndex: 'photos',
                width: 200,
                render: (_, record) =>
                  record.photos?.length > 0 ? (
                    <Image.PreviewGroup>
                      <Space>
                        {record.photos.map((p) => (
                          <Image
                            key={p.id}
                            src={p.photo_url}
                            width={40}
                            height={40}
                            style={{ objectFit: 'cover', borderRadius: 4 }}
                          />
                        ))}
                      </Space>
                    </Image.PreviewGroup>
                  ) : (
                    '0 张'
                  ),
              },
              {
                title: '操作',
                width: 100,
                render: (_, record) => (
                  <Button
                    type="link"
                    size="small"
                    onClick={() => {
                      setPhotoRecordId(record.id);
                      setPhotoModalOpen(true);
                    }}
                  >
                    添加照片
                  </Button>
                ),
              },
            ]}
          />
        </Card>
      )}

      <Modal
        title="添加装柜照片"
        open={photoModalOpen}
        onOk={handleAddPhoto}
        onCancel={() => { setPhotoModalOpen(false); setPhotoUrl(''); setPhotoDesc(''); }}
        okText="确定"
        cancelText="取消"
      >
        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4 }}>照片URL *</label>
          <Input
            value={photoUrl}
            onChange={(e) => setPhotoUrl(e.target.value)}
            placeholder="https://example.com/photo.jpg"
          />
        </div>
        <div>
          <label style={{ display: 'block', marginBottom: 4 }}>描述</label>
          <Input
            value={photoDesc}
            onChange={(e) => setPhotoDesc(e.target.value)}
            placeholder="照片描述（可选）"
          />
        </div>
      </Modal>

      <InventoryBatchPicker
        open={batchPickerOpen}
        onClose={() => setBatchPickerOpen(false)}
        onSelect={handleBatchSelect}
      />
    </PageContainer>
  );
}
