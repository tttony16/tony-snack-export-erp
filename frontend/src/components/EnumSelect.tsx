import { Select, type SelectProps } from 'antd';

interface EnumSelectProps extends Omit<SelectProps, 'options'> {
  enumMap: Record<string, string>;
}

export default function EnumSelect({ enumMap, ...props }: EnumSelectProps) {
  const options = Object.entries(enumMap).map(([value, label]) => ({
    value,
    label,
  }));
  return <Select options={options} {...props} />;
}
