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

        <a-form-item label="自动刷新">
          <a-switch
            v-model="autoRefresh"
            checked-children="开"
            un-checked-children="关"
            @change="toggleAutoRefresh"
          />
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button type="primary" @click="handleQuery">查询</a-button>
            <a-button @click="handleReset">重置</a-button>
            <a-button @click="handleExport" :loading="exporting">
              {{ exporting ? '导出中...' : '导出' }}
            </a-button>
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
        :scroll="{ x: 1400 }"
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
import { ref, reactive, onMounted, onUnmounted, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import dayjs from 'dayjs'
import { useUserStore } from '@/stores/user'
import { queryAuditLogs, getAuditStatistics, exportAuditLogs } from '@/api/permission-audit'
import { getUserList } from '@/api/user'

const userStore = useUserStore()

// 状态
const loading = ref(false)
const exporting = ref(false) // MEDIUM-3 FIXED: 添加导出状态
const autoRefresh = ref(false) // LOW-2 FIXED: 添加自动刷新开关
const refreshTimer = ref<any>(null) // 定时器引用
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

// LOW-1 FIXED: 提取日期范围处理为工具函数，避免重复代码
function formatDateRange(dateRange: any[]): { start_date?: string; end_date?: string } {
  if (!dateRange || dateRange.length !== 2) {
    return {}
  }
  return {
    start_date: dayjs(dateRange[0]).format('YYYY-MM-DD'),
    end_date: dayjs(dateRange[1]).format('YYYY-MM-DD'),
  }
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

    // LOW-1 FIXED: 使用工具函数处理日期范围
    const dateRangeParams = formatDateRange(filters.dateRange)
    Object.assign(params, dateRangeParams)

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
    // MEDIUM-2 FIXED: 改进错误处理，根据不同状态码显示友好提示
    const status = err.response?.status
    if (status === 401) {
      Message.error('会话已过期，请重新登录')
      // 可以在这里跳转到登录页
      // router.push('/login')
    } else if (status === 403) {
      Message.error('没有权限访问该资源')
    } else if (status === 404) {
      Message.error('请求的资源不存在')
    } else if (status === 500) {
      Message.error('服务器错误，请稍后重试')
    } else if (status === 503) {
      Message.error('服务暂时不可用，请稍后重试')
    } else {
      Message.error(err.message || '查询失败，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

// 查询统计信息
async function queryStatistics() {
  try {
    // LOW-1 FIXED: 使用工具函数处理日期范围
    const params = formatDateRange(filters.dateRange)

    const response = await getAuditStatistics(params)

    if (response.success) {
      statistics.value = response.data
    }
  } catch (err: any) {
    // MEDIUM-2 FIXED: 统计查询错误处理（静默失败，不影响主功能）
    console.error('Failed to query statistics:', err)
    // 可以选择显示非侵入式提示
    // Message.warning('统计信息获取失败，已使用缓存数据')
  }
}

// 加载用户列表
async function loadUserList() {
  try {
    const response = await getUserList()
    if (response.success) {
      userList.value = response.data || []
    }
  } catch (err: any) {
    // MEDIUM-2 FIXED: 用户列表加载错误处理
    console.error('Failed to load user list:', err)
    Message.warning('用户列表加载失败，请刷新页面重试')
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
  // MEDIUM-3 FIXED: 添加导出进度提示
  exporting.value = true
  const loadingMsg = Message.loading({
    content: '正在导出审计记录，请稍候...',
    duration: 0, // 不自动消失
  })

  try {
    const params: any = { format: 'csv' }

    if (filters.user_id) {
      params.user_id = filters.user_id
    }

    // LOW-1 FIXED: 使用工具函数处理日期范围
    const dateRangeParams = formatDateRange(filters.dateRange)
    Object.assign(params, dateRangeParams)

    const response = await exportAuditLogs(params)

    // 创建下载链接
    const blob = new Blob([response], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `permission_audit_${dayjs().format('YYYYMMDDHHmmss')}.csv`
    link.click()
    window.URL.revokeObjectURL(url)

    loadingMsg.close()
    Message.success('导出成功')
  } catch (err: any) {
    loadingMsg.close()
    // MEDIUM-2 FIXED: 改进导出错误处理
    const status = err.response?.status
    if (status === 401) {
      Message.error('会话已过期，请重新登录')
    } else if (status === 403) {
      Message.error('没有导出权限')
    } else if (status === 500) {
      Message.error('服务器错误，导出失败')
    } else {
      Message.error(err.message || '导出失败，请稍后重试')
    }
  } finally {
    exporting.value = false
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

// LOW-2 FIXED: 自动刷新功能
function toggleAutoRefresh(value: boolean) {
  if (value) {
    // 开启自动刷新（每 5 分钟）
    refreshTimer.value = setInterval(
      () => {
        queryAuditRecords()
        Message.success('数据已自动刷新')
      },
      5 * 60 * 1000
    )
  } else {
    // 关闭自动刷新
    if (refreshTimer.value) {
      clearInterval(refreshTimer.value)
      refreshTimer.value = null
    }
  }
}

// 生命周期
onMounted(() => {
  loadUserList()
  queryAuditRecords()
})

// LOW-2 FIXED: 组件卸载时清理定时器
onUnmounted(() => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
})
</script>

<style scoped lang="less">
.permission-audit {
  .audit-filters {
    margin-bottom: 16px;
  }
}
</style>
