<template>
  <div class="permission-audit">
    <a-card title="权限审计" :bordered="false">
      <!-- 筛选条件 -->
      <a-form layout="inline" class="audit-filters">
        <a-form-item label="用户">
          <a-select
            v-model="filters.user_id"
            placeholder="选择用户"
            allow-clear
            style="width: 200px"
          >
            <a-option v-for="user in userList" :key="user.id" :value="user.id">
              {{ user.username }} ({{ user.real_name }})
            </a-option>
          </a-select>
        </a-form-item>

        <a-form-item label="日期范围">
          <a-range-picker
            v-model="filters.dateRange"
            :shortcuts="dateRangeShortcuts"
            style="width: 240px"
          />
        </a-form-item>

        <a-form-item label="异常类型">
          <a-select
            v-model="filters.anomaly_type"
            placeholder="选择异常类型"
            allow-clear
            style="width: 200px"
          >
            <a-option value="unauthorized_access">未授权访问</a-option>
            <a-option value="frequent_access">频繁访问</a-option>
            <a-option value="location_anomaly">异地访问</a-option>
            <a-option value="privilege_escalation">越权访问</a-option>
          </a-select>
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button type="primary" @click="handleQuery">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
            <a-button @click="handleExport">导出</a-button>
          </a-space>
        </a-form-item>
      </a-form>

      <!-- 统计信息 -->
      <a-row :gutter="16" style="margin-top: 16px">
        <a-col :span="6">
          <a-statistic title="总记录数" :value="statistics.total_records" />
        </a-col>
        <a-col :span="6">
          <a-statistic
            title="异常记录数"
            :value="statistics.anomaly_count"
            :value-style="{ color: '#f53f3f' }"
          />
        </a-col>
        <a-col :span="6">
          <a-statistic title="异常率" :value="statistics.anomaly_rate" suffix="%" :precision="2" />
        </a-col>
      </a-row>

      <!-- 审计记录表格 -->
      <a-table
        :data="auditRecords"
        :columns="columns"
        :loading="loading"
        :pagination="pagination"
        @page-change="handlePageChange"
        @sorter-change="handleSortChange"
        size="small"
        style="margin-top: 16px"
      >
        <!-- 异常标记 -->
        <template #is_anomaly="{ record }">
          <a-tag v-if="record.is_anomaly" color="red">
            {{ getAnomalyTypeName(record.anomaly_type) }}
          </a-tag>
          <a-tag v-else color="green">正常</a-tag>
        </template>

        <!-- 时间格式化 -->
        <template #timestamp="{ record }">
          {{ formatTimestamp(record.timestamp) }}
        </template>

        <!-- 详情 -->
        <template #details="{ record }">
          <a-popover position="left" v-if="record.details">
            <a-button type="text" size="small">查看详情</a-button>
            <template #content>
              <pre style="max-width: 400px; max-height: 300px; overflow: auto">{{
                JSON.stringify(JSON.parse(record.details), null, 2)
              }}</pre>
            </template>
          </a-popover>
          <span v-else>-</span>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import { queryAuditLogs, getAuditStatistics, exportAuditLogs } from '@/api/permission-audit'
import { getUserList } from '@/api/user'

const userStore = useUserStore()

// 状态
const loading = ref(false)
const userList = ref<any[]>([])
const auditRecords = ref<any[]>([])
const statistics = ref({
  total_records: 0,
  anomaly_count: 0,
  anomaly_rate: 0,
})

// 筛选条件
const filters = reactive({
  user_id: undefined as string | undefined,
  dateRange: [] as any[],
  anomaly_type: undefined as string | undefined,
})

// 日期范围快捷选项
const dateRangeShortcuts = [
  {
    name: '今天',
    value: () => [dayjs().startOf('day'), dayjs().endOf('day')],
  },
  {
    name: '本周',
    value: () => [dayjs().startOf('week'), dayjs().endOf('week')],
  },
  {
    name: '本月',
    value: () => [dayjs().startOf('month'), dayjs().endOf('month')],
  },
  {
    name: '近 7 天',
    value: () => [dayjs().subtract(6, 'day'), dayjs()],
  },
  {
    name: '近 30 天',
    value: () => [dayjs().subtract(29, 'day'), dayjs()],
  },
]

// 表格列
const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 80 },
  { title: '用户 ID', dataIndex: 'user_id', key: 'user_id', width: 120 },
  { title: '角色', dataIndex: 'role', key: 'role', width: 100 },
  { title: '资源', dataIndex: 'resource', key: 'resource', width: 120 },
  { title: '操作', dataIndex: 'action', key: 'action', width: 100 },
  { title: 'IP 地址', dataIndex: 'ip_address', key: 'ip_address', width: 140 },
  {
    title: '异常标记',
    dataIndex: 'is_anomaly',
    key: 'is_anomaly',
    slotName: 'is_anomaly',
    width: 120,
  },
  {
    title: '时间',
    dataIndex: 'timestamp',
    key: 'timestamp',
    slotName: 'timestamp',
    width: 180,
    sortable: { sortDirections: ['ascend', 'descend'] },
  },
  { title: '详情', dataIndex: 'details', key: 'details', slotName: 'details', width: 100 },
]

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showTotal: true,
  showPageSize: true,
})

// 排序
const sortInfo = ref({ field: 'timestamp', direction: 'desc' })

// 获取异常类型名称
function getAnomalyTypeName(type: string | null): string {
  const typeNames: Record<string, string> = {
    unauthorized_access: '未授权访问',
    frequent_access: '频繁访问',
    location_anomaly: '异地访问',
    privilege_escalation: '越权访问',
  }
  return typeNames[type || ''] || '未知异常'
}

// 格式化时间戳
function formatTimestamp(timestamp: string): string {
  return dayjs(timestamp).format('YYYY-MM-DD HH:mm:ss')
}

// 查询审计记录
async function queryAuditRecords() {
  loading.value = true
  try {
    const params: any = {
      page: pagination.current,
      page_size: pagination.pageSize,
      sort_by: sortInfo.value.field,
      sort_order: sortInfo.value.direction === 'descend' ? 'desc' : 'asc',
    }

    if (filters.user_id) {
      params.user_id = filters.user_id
    }

    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = dayjs(filters.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(filters.dateRange[1]).format('YYYY-MM-DD')
    }

    if (filters.anomaly_type) {
      params.anomaly_type = filters.anomaly_type
    }

    const response = await queryAuditLogs(params)

    if (response.success) {
      auditRecords.value = response.data.records
      pagination.total = response.data.total
      pagination.current = response.data.page

      // 同时更新统计信息
      await queryStatistics()
    } else {
      Message.error(response.error || '查询失败')
    }
  } catch (err: any) {
    Message.error(err.message || '查询失败')
  } finally {
    loading.value = false
  }
}

// 查询统计信息
async function queryStatistics() {
  try {
    const params: any = {}

    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = dayjs(filters.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(filters.dateRange[1]).format('YYYY-MM-DD')
    }

    const response = await getAuditStatistics(params)

    if (response.success) {
      statistics.value = response.data
    }
  } catch (err) {
    console.error('Failed to query statistics:', err)
  }
}

// 加载用户列表
async function loadUserList() {
  try {
    const response = await getUserList()
    if (response.success) {
      userList.value = response.data || []
    }
  } catch (err) {
    console.error('Failed to load user list:', err)
  }
}

// 处理查询
function handleQuery() {
  pagination.current = 1
  queryAuditRecords()
}

// 处理重置
function handleReset() {
  filters.user_id = undefined
  filters.dateRange = []
  filters.anomaly_type = undefined
  pagination.current = 1
  queryAuditRecords()
}

// 处理导出
async function handleExport() {
  try {
    const params: any = { format: 'csv' }

    if (filters.user_id) {
      params.user_id = filters.user_id
    }

    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = dayjs(filters.dateRange[0]).format('YYYY-MM-DD')
      params.end_date = dayjs(filters.dateRange[1]).format('YYYY-MM-DD')
    }

    const response = await exportAuditLogs(params)

    // 创建下载链接
    const blob = new Blob([response], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `permission_audit_${dayjs().format('YYYYMMDDHHmmss')}.csv`
    link.click()
    window.URL.revokeObjectURL(url)

    Message.success('导出成功')
  } catch (err: any) {
    Message.error(err.message || '导出失败')
  }
}

// 处理分页变更
function handlePageChange(page: number) {
  pagination.current = page
  queryAuditRecords()
}

// 处理排序变更
function handleSortChange(sorter: any) {
  sortInfo.value = {
    field: sorter.field,
    direction: sorter.direction,
  }
  queryAuditRecords()
}

// 生命周期
onMounted(() => {
  loadUserList()
  queryAuditRecords()
})
</script>

<style scoped lang="less">
.permission-audit {
  .audit-filters {
    margin-bottom: 16px;
  }
}
</style>
