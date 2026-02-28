import { useState, useEffect, useCallback } from 'react';
import { Select, type SelectProps } from 'antd';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface EntitySelectProps extends Omit<SelectProps, 'options' | 'onSearch' | 'loading'> {
  fetchFn: (params: { keyword?: string; page_size?: number }) => Promise<{ items: any[] }>;
  labelField: string;
  valueField?: string;
}

export default function EntitySelect({
  fetchFn,
  labelField,
  valueField = 'id',
  ...props
}: EntitySelectProps) {
  const [options, setOptions] = useState<{ value: string; label: string }[]>([]);
  const [loading, setLoading] = useState(false);

  const search = useCallback(
    async (keyword?: string) => {
      setLoading(true);
      try {
        const data = await fetchFn({ keyword, page_size: 50 });
        setOptions(
          data.items.map((item: Record<string, unknown>) => ({
            value: String(item[valueField]),
            label: String(item[labelField]),
          })),
        );
      } finally {
        setLoading(false);
      }
    },
    [fetchFn, labelField, valueField],
  );

  useEffect(() => {
    search();
  }, [search]);

  return (
    <Select
      showSearch
      filterOption={false}
      onSearch={search}
      loading={loading}
      options={options}
      popupMatchSelectWidth={false}
      style={{ width: '100%', ...props.style }}
      dropdownStyle={{ minWidth: 260 }}
      {...props}
    />
  );
}
