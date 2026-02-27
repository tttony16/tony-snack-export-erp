import { Button, type ButtonProps } from 'antd';
import { usePermission } from '@/hooks/usePermission';

interface PermissionButtonProps extends ButtonProps {
  permission: string;
}

export default function PermissionButton({ permission, ...props }: PermissionButtonProps) {
  const { hasPermission } = usePermission();
  if (!hasPermission(permission)) return null;
  return <Button {...props} />;
}
