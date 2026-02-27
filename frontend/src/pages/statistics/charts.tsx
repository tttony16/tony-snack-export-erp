import { Column, Bar } from '@ant-design/charts';

interface BarChartItem {
  group_key: string;
  value: number;
  label?: string;
}

interface ColumnChartProps {
  data: BarChartItem[];
  xField?: string;
  yField?: string;
  title?: string;
}

export function TrendChart({ data, xField = 'group_key', yField = 'value' }: ColumnChartProps) {
  return (
    <Column
      data={data}
      xField={xField}
      yField={yField}
      height={300}
      label={{
        position: 'top',
      }}
    />
  );
}

interface RankingChartProps {
  data: BarChartItem[];
  xField?: string;
  yField?: string;
}

export function RankingChart({ data, xField = 'value', yField = 'group_key' }: RankingChartProps) {
  return (
    <Bar
      data={data}
      xField={xField}
      yField={yField}
      height={300}
      label={{
        position: 'right',
      }}
    />
  );
}
