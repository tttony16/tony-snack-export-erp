import { useState, useEffect, useCallback } from 'react';
import { Select, type SelectProps } from 'antd';

// eslint-disable-next-line @typescript-eslint/no-explicit-any
interface EntitySelectProps extends Omit<SelectProps, 'options' | 'onSearch' | 'loading'> {
  fetchFn: (params: Record<string, unknown>) => Promise<{ items: any[] }>;
  labelField: string;
  valueField?: string;
  /** Extra query params merged into every fetch call */
  extraParams?: Record<string, unknown>;
}

export default function EntitySelect({
  fetchFn,
  labelField,
  valueField = 'id',
  extraParams,
  ...props
}: EntitySelectProps) {
  const [options, setOptions] = useState<{ value: string; label: string }[]>([]);
  const [loading, setLoading] = useState(false);

  // Stable serialized key for extraParams to use in deps
  const extraKey = JSON.stringify(extraParams || {});

  const search = useCallback(
    async (keyword?: string) => {
      setLoading(true);
      try {
        const data = await fetchFn({ keyword, page_size: 50, ...extraParams });
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [fetchFn, labelField, valueField, extraKey],
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
