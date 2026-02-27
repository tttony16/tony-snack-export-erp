import { Input } from 'antd';
import { useNavigate } from 'react-router-dom';

export default function GlobalSearch() {
  const navigate = useNavigate();

  const handleSearch = (value: string) => {
    const v = value.trim();
    if (!v) return;

    const upper = v.toUpperCase();
    if (upper.startsWith('SO-')) {
      navigate(`/sales-orders?keyword=${encodeURIComponent(v)}`);
    } else if (upper.startsWith('PO-')) {
      navigate(`/purchase-orders?keyword=${encodeURIComponent(v)}`);
    } else if (upper.startsWith('CL-') || upper.startsWith('CP-')) {
      navigate(`/containers?keyword=${encodeURIComponent(v)}`);
    } else if (upper.startsWith('LOG-') || upper.startsWith('LG-')) {
      navigate(`/logistics?keyword=${encodeURIComponent(v)}`);
    } else if (upper.startsWith('RCV-') || upper.startsWith('RN-')) {
      navigate(`/warehouse/receiving-notes?keyword=${encodeURIComponent(v)}`);
    } else {
      navigate(`/products?keyword=${encodeURIComponent(v)}`);
    }
  };

  return (
    <Input.Search
      placeholder="搜索单号/商品名..."
      onSearch={handleSearch}
      style={{ width: 250 }}
      allowClear
    />
  );
}
