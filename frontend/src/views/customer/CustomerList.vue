<!--
客户列表页面 - 集成数据权限

功能:
- 显示客户列表（根据数据权限过滤）
- 数据范围选择器
- 分页和筛选
- 越权访问处理

Story 1.4: Data Permission
-->
<template>
  <div class="customer-list-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2 class="page-title">客户管理</h2>

      <!-- 数据范围选择器 -->
      <DataScopeSelector :show-label="true" :show-tip="true" @change="handleDataScopeChange" />
    </div>

    <!-- 操作栏 -->
    <div class="action-bar">
      <el-button type="primary" @click="handleCreate">
        <el-icon><Plus /></el-icon>
        新建客户
      </el-button>

      <el-button @click="refreshList">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>

      <!-- 筛选器 -->
      <el-input
        v-model="searchKeyword"
        placeholder="搜索客户名称"
        clearable
        @input="handleSearch"
      />

      <el-select v-model="filterStatus" placeholder="客户状态" clearable @change="handleSearch">
        <el-option label="活跃" value="active" />
        <el-option label="非活跃" value="inactive" />
        <el-option label="潜在客户" value="lead" />
      </el-select>
    </div>

    <!-- 客户列表 -->
    <el-table
      v-loading="isLoading"
      :data="customers"
      border
      stripe
      style="width: 100%"
      @row-click="handleRowClick"
    >
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="客户名称" min-width="200" />
      <el-table-column prop="contact_name" label="联系人" width="120" />
      <el-table-column prop="contact_email" label="邮箱" width="200" />
      <el-table-column prop="contact_phone" label="电话" width="150" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="sales_rep_id" label="销售代表" width="120">
        <template #default="{ row }">
          {{ row.sales_rep?.username || row.sales_rep_id }}
        </template>
      </el-table-column>
      <el-table-column prop="org_id" label="组织" width="100">
        <template #default="{ row }">
          {{ row.organization?.name || row.org_id }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" @click.stop="handleView(row)"> 详情 </el-button>
          <el-button link type="primary" @click.stop="handleEdit(row)"> 编辑 </el-button>
          <el-button link type="danger" @click.stop="handleDelete(row)"> 删除 </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <div class="pagination-container">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 权限错误提示 -->
    <el-dialog v-model="showPermissionError" title="权限不足" width="400px">
      <div class="permission-error-content">
        <el-icon :size="48" color="#f56c6c">
          <Warning-Filled />
        </el-icon>
        <p>{{ permissionErrorMessage }}</p>
      </div>
      <template #footer>
        <el-button @click="showPermissionError = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Refresh, WarningFilled } from '@element-plus/icons-vue'
import DataScopeSelector from '@/components/business/permission/DataScopeSelector.vue'
import { useDataPermissionStore } from '@/stores/data-permission'
import { canAccessCustomer } from '@/utils/data-permission-check'
import { getCustomersWithPermission, getCustomerById } from '@/api/data-permission'
import type { DataScope } from '@/types/data-permission'

// ==================== State ====================

const router = useRouter()
const dataPermissionStore = useDataPermissionStore()

const isLoading = ref(false)
const customers = ref<any[]>([])
const searchKeyword = ref('')
const filterStatus = ref('')

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0,
})

const showPermissionError = ref(false)
const permissionErrorMessage = ref('')

// ==================== Methods ====================

/**
 * 加载客户列表
 */
async function loadCustomers() {
  isLoading.value = true

  try {
    const response = await getCustomersWithPermission({
      page: pagination.page,
      page_size: pagination.page_size,
      status: filterStatus.value || undefined,
    })

    customers.value = response.data || []
    pagination.total = response.meta?.total || 0
  } catch (error) {
    if ((error as any).response?.status === 403) {
      // 权限错误
      showPermissionError.value = true
      permissionErrorMessage.value = '您没有权限查看这些客户'
    } else {
      ElMessage.error('加载客户列表失败')
    }
  } finally {
    isLoading.value = false
  }
}

/**
 * 刷新列表
 */
function refreshList() {
  pagination.page = 1
  loadCustomers()
}

/**
 * 处理数据范围变化
 */
async function handleDataScopeChange(scope: DataScope, orgId?: number) {
  ElMessage.success(
    `已切换到${scope === 'organization' ? '本组织' : scope === 'personal' ? '个人' : '全部'}数据范围`
  )
  refreshList()
}

/**
 * 处理搜索
 */
function handleSearch() {
  refreshList()
}

/**
 * 处理分页变化
 */
function handlePageChange(page: number) {
  pagination.page = page
  loadCustomers()
}

/**
 * 处理每页数量变化
 */
function handleSizeChange(size: number) {
  pagination.page_size = size
  pagination.page = 1
  loadCustomers()
}

/**
 * 新建客户
 */
function handleCreate() {
  router.push('/customers/new')
}

/**
 * 查看详情
 */
async function handleView(row: any) {
  try {
    // 检查数据权限
    if (!canAccessCustomer(row.id, row.org_id, row.sales_rep_id)) {
      showPermissionError.value = true
      permissionErrorMessage.value = '您没有权限查看此客户'
      return
    }

    const response = await getCustomerById(row.id)
    router.push(`/customers/${row.id}`)
  } catch (error) {
    if ((error as any).response?.status === 403) {
      showPermissionError.value = true
      permissionErrorMessage.value = '您没有权限查看此客户'
    } else {
      ElMessage.error('加载客户详情失败')
    }
  }
}

/**
 * 编辑客户
 */
function handleEdit(row: any) {
  if (!canAccessCustomer(row.id, row.org_id, row.sales_rep_id)) {
    showPermissionError.value = true
    permissionErrorMessage.value = '您没有权限编辑此客户'
    return
  }
  router.push(`/customers/${row.id}/edit`)
}

/**
 * 删除客户
 */
async function handleDelete(row: any) {
  if (!canAccessCustomer(row.id, row.org_id, row.sales_rep_id)) {
    showPermissionError.value = true
    permissionErrorMessage.value = '您没有权限删除此客户'
    return
  }

  try {
    await ElMessageBox.confirm('确定要删除该客户吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    // TODO: 调用删除 API
    ElMessage.success('删除成功')
    refreshList()
  } catch (error) {
    if ((error as any).response?.status === 403) {
      showPermissionError.value = true
      permissionErrorMessage.value = '您没有权限删除此客户'
    }
  }
}

/**
 * 处理行点击
 */
function handleRowClick(row: any) {
  handleView(row)
}

/**
 * 获取状态类型
 */
function getStatusType(status: string): 'success' | 'info' | 'warning' | 'danger' {
  switch (status) {
    case 'active':
      return 'success'
    case 'inactive':
      return 'info'
    case 'lead':
      return 'warning'
    default:
      return 'info'
  }
}

/**
 * 获取状态标签
 */
function getStatusLabel(status: string): string {
  switch (status) {
    case 'active':
      return '活跃'
    case 'inactive':
      return '非活跃'
    case 'lead':
      return '潜在客户'
    default:
      return status
  }
}

// ==================== Lifecycle ====================

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped lang="scss">
.customer-list-page {
  padding: 20px;

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .page-title {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
  }

  .action-bar {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;

    .el-input {
      width: 240px;
    }

    .el-select {
      width: 150px;
    }
  }

  .pagination-container {
    display: flex;
    justify-content: flex-end;
    margin-top: 20px;
  }

  .permission-error-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;

    p {
      margin: 0;
      font-size: 16px;
      color: #606266;
    }
  }
}
</style>
