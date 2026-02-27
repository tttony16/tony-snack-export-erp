import { useState, useEffect } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Table, Input, message, Space } from 'antd';
import { listConfigs, updateConfig } from '@/api/system';
import type { SystemConfigRead } from '@/types/models';
import { formatDateTime } from '@/utils/format';

export default function SystemConfigsPage() {
  const [configs, setConfigs] = useState<SystemConfigRead[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingKey, setEditingKey] = useState<string>('');
  const [editValue, setEditValue] = useState<string>('');

  const load = async () => {
    setLoading(true);
    try {
      const data = await listConfigs();
      setConfigs(Array.isArray(data) ? data : []);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const handleSave = async (key: string) => {
    try {
      let parsedValue: unknown = editValue;
      try { parsedValue = JSON.parse(editValue); } catch { /* keep as string */ }
      await updateConfig(key, { config_value: parsedValue });
      message.success('保存成功');
      setEditingKey('');
      load();
    } catch {
      // error handled by interceptor
    }
  };

  return (
    <PageContainer>
      <Table<SystemConfigRead>
        dataSource={configs}
        rowKey="config_key"
        loading={loading}
        pagination={false}
        columns={[
          { title: '配置键', dataIndex: 'config_key', width: 200 },
          {
            title: '配置值',
            dataIndex: 'config_value',
            render: (_, record) => {
              if (editingKey === record.config_key) {
                return (
                  <Input
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    onPressEnter={() => handleSave(record.config_key)}
                    style={{ width: 300 }}
                  />
                );
              }
              return typeof record.config_value === 'object'
                ? JSON.stringify(record.config_value)
                : String(record.config_value);
            },
          },
          { title: '描述', dataIndex: 'description' },
          {
            title: '更新时间',
            dataIndex: 'updated_at',
            width: 170,
            render: (_, r) => formatDateTime(r.updated_at),
          },
          {
            title: '操作',
            width: 120,
            render: (_, record) => {
              if (editingKey === record.config_key) {
                return (
                  <Space>
                    <a onClick={() => handleSave(record.config_key)}>保存</a>
                    <a onClick={() => setEditingKey('')}>取消</a>
                  </Space>
                );
              }
              return (
                <a
                  onClick={() => {
                    setEditingKey(record.config_key);
                    setEditValue(
                      typeof record.config_value === 'object'
                        ? JSON.stringify(record.config_value)
                        : String(record.config_value),
                    );
                  }}
                >
                  编辑
                </a>
              );
            },
          },
        ]}
      />
    </PageContainer>
  );
}
