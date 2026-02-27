import { useState, useEffect } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Tabs, DatePicker, Space, Select, Spin, Card, Empty } from 'antd';
import dayjs from 'dayjs';
import {
  getSalesSummary,
  getPurchaseSummary,
  getContainerSummary,
  getCustomerRanking,
  getProductRanking,
} from '@/api/statistics';
import { TrendChart, RankingChart } from './charts';

const { RangePicker } = DatePicker;

interface ChartData {
  group_key: string;
  value: number;
}

export default function StatisticsPage() {
  const [activeTab, setActiveTab] = useState('sales');
  const [groupBy, setGroupBy] = useState('month');
  const [dateRange, setDateRange] = useState<[string, string]>([
    dayjs().subtract(6, 'month').format('YYYY-MM-DD'),
    dayjs().format('YYYY-MM-DD'),
  ]);
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(false);

  const params = {
    date_from: dateRange[0],
    date_to: dateRange[1],
    group_by: groupBy,
  };

  const loadData = async () => {
    setLoading(true);
    try {
      let items: ChartData[] = [];
      switch (activeTab) {
        case 'sales': {
          const res = await getSalesSummary(params);
          items = res.items.map((i) => ({ group_key: i.group_key, value: Number(i.total_amount) }));
          break;
        }
        case 'purchase': {
          const res = await getPurchaseSummary(params);
          items = res.items.map((i) => ({ group_key: i.group_key, value: Number(i.total_amount) }));
          break;
        }
        case 'container': {
          const res = await getContainerSummary(params);
          items = res.items.map((i) => ({ group_key: i.group_key, value: i.container_count }));
          break;
        }
        case 'customer': {
          const res = await getCustomerRanking(params);
          items = res.items.map((i) => ({ group_key: i.customer_name || i.customer_id, value: Number(i.total_amount) }));
          break;
        }
        case 'product': {
          const res = await getProductRanking(params);
          items = res.items.map((i) => ({ group_key: i.product_name || i.product_id, value: i.total_quantity }));
          break;
        }
      }
      setData(items);
    } catch {
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [activeTab, groupBy, dateRange[0], dateRange[1]]); // eslint-disable-line react-hooks/exhaustive-deps

  const isRanking = activeTab === 'customer' || activeTab === 'product';

  return (
    <PageContainer
      title="统计报表"
      extra={
        <Space>
          <RangePicker
            value={[dayjs(dateRange[0]), dayjs(dateRange[1])]}
            onChange={(dates) => {
              if (dates?.[0] && dates?.[1]) {
                setDateRange([dates[0].format('YYYY-MM-DD'), dates[1].format('YYYY-MM-DD')]);
              }
            }}
          />
          {!isRanking && (
            <Select
              value={groupBy}
              onChange={setGroupBy}
              options={[
                { value: 'month', label: '按月' },
                { value: 'week', label: '按周' },
                { value: 'day', label: '按天' },
              ]}
              style={{ width: 100 }}
            />
          )}
        </Space>
      }
    >
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={[
          { key: 'sales', label: '销售统计' },
          { key: 'purchase', label: '采购统计' },
          { key: 'container', label: '排柜统计' },
          { key: 'customer', label: '客户排名' },
          { key: 'product', label: '商品排名' },
        ]}
      />
      <Card>
        {loading ? (
          <Spin style={{ display: 'block', margin: '50px auto' }} />
        ) : data.length === 0 ? (
          <Empty description="暂无数据" />
        ) : isRanking ? (
          <RankingChart data={data} />
        ) : (
          <TrendChart data={data} />
        )}
      </Card>
    </PageContainer>
  );
}
