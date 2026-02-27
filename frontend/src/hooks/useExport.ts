import { useState } from 'react';
import { message } from 'antd';
import { downloadFile } from '@/utils/download';

export function useExport(url: string, defaultFilename = 'export.xlsx') {
  const [exporting, setExporting] = useState(false);

  const handleExport = async (params?: Record<string, unknown>, filename?: string) => {
    setExporting(true);
    try {
      const query = params
        ? '?' + new URLSearchParams(
            Object.entries(params)
              .filter(([, v]) => v != null)
              .map(([k, v]) => [k, String(v)])
          ).toString()
        : '';
      await downloadFile(url + query, filename || defaultFilename);
      message.success('导出成功');
    } catch {
      message.error('导出失败');
    } finally {
      setExporting(false);
    }
  };

  return { exporting, handleExport };
}
