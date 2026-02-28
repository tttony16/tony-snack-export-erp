import { useEffect, useState } from 'react';
import { PageContainer } from '@ant-design/pro-components';
import { Button, Card, Input, InputNumber, Modal, Space, Spin, Tree, message, Popconfirm } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { getCategoryTree, createCategory, updateCategory, deleteCategory } from '@/api/productCategories';
import type { ProductCategoryTreeNode } from '@/types/models';
import type { DataNode } from 'antd/es/tree';

export default function CategoriesPage() {
  const [tree, setTree] = useState<ProductCategoryTreeNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingNode, setEditingNode] = useState<ProductCategoryTreeNode | null>(null);
  const [parentNode, setParentNode] = useState<ProductCategoryTreeNode | null>(null);
  const [formName, setFormName] = useState('');
  const [formSortOrder, setFormSortOrder] = useState(0);

  const loadTree = async () => {
    setLoading(true);
    try {
      const data = await getCategoryTree();
      setTree(data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTree();
  }, []);

  const toTreeData = (nodes: ProductCategoryTreeNode[]): DataNode[] =>
    nodes.map((node) => ({
      key: node.id,
      title: (
        <Space>
          <span>{node.name}</span>
          {node.level < 3 && (
            <Button
              type="link"
              size="small"
              icon={<PlusOutlined />}
              onClick={(e) => {
                e.stopPropagation();
                setParentNode(node);
                setEditingNode(null);
                setFormName('');
                setFormSortOrder(0);
                setModalOpen(true);
              }}
            >
              添加子品类
            </Button>
          )}
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              setEditingNode(node);
              setParentNode(null);
              setFormName(node.name);
              setFormSortOrder(node.sort_order);
              setModalOpen(true);
            }}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定删除该品类？"
            description="将同时删除所有子品类"
            onConfirm={async (e) => {
              e?.stopPropagation();
              try {
                await deleteCategory(node.id);
                message.success('删除成功');
                loadTree();
              } catch (err: unknown) {
                const errorMsg = err instanceof Error ? err.message : '删除失败';
                message.error(errorMsg);
              }
            }}
            onCancel={(e) => e?.stopPropagation()}
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
              onClick={(e) => e.stopPropagation()}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
      children: node.children.length > 0 ? toTreeData(node.children) : undefined,
    }));

  const handleSubmit = async () => {
    if (!formName.trim()) {
      message.warning('请输入品类名称');
      return;
    }

    try {
      if (editingNode) {
        await updateCategory(editingNode.id, {
          name: formName,
          sort_order: formSortOrder,
        });
        message.success('更新成功');
      } else {
        await createCategory({
          name: formName,
          parent_id: parentNode?.id,
          sort_order: formSortOrder,
        });
        message.success('创建成功');
      }
      setModalOpen(false);
      loadTree();
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : '操作失败';
      message.error(errorMsg);
    }
  };

  return (
    <PageContainer>
      <Card
        title="品类管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setParentNode(null);
              setEditingNode(null);
              setFormName('');
              setFormSortOrder(0);
              setModalOpen(true);
            }}
          >
            添加一级品类
          </Button>
        }
      >
        <Spin spinning={loading}>
          <Tree
            treeData={toTreeData(tree)}
            defaultExpandAll
            blockNode
            showLine
          />
        </Spin>
      </Card>

      <Modal
        title={editingNode ? '编辑品类' : parentNode ? `添加子品类（${parentNode.name}）` : '添加一级品类'}
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={handleSubmit}
        destroyOnClose
      >
        <Space direction="vertical" style={{ width: '100%' }} size="middle">
          <div>
            <div style={{ marginBottom: 4 }}>品类名称</div>
            <Input
              value={formName}
              onChange={(e) => setFormName(e.target.value)}
              placeholder="请输入品类名称"
              maxLength={100}
            />
          </div>
          <div>
            <div style={{ marginBottom: 4 }}>排序</div>
            <InputNumber
              value={formSortOrder}
              onChange={(v) => setFormSortOrder(v ?? 0)}
              min={0}
              style={{ width: '100%' }}
            />
          </div>
        </Space>
      </Modal>
    </PageContainer>
  );
}
