import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright 配置 - 内部运营中台客户信息管理与运营系统
 * 
 * 技术栈：Vue 3 + Arco Design + TypeScript
 * 测试策略：E2E 测试 + API 测试 + 视觉回归测试
 */

export default defineConfig({
  // 测试目录配置
  testDir: './e2e',
  
  // 完全并行运行测试
  fullyParallel: true,
  
  // 每个测试的重试次数（CI 环境中）
  retries: process.env.CI ? 2 : 0,
  
  // 并行工作数（CI 环境中优化）
  workers: process.env.CI ? '100%' : undefined,
  
  // 报告器配置：HTML + JUnit + 控制台
  reporter: [
    ['html', { outputFolder: 'playwright-report', open: 'never' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
    ['list']
  ],
  
  // 共享配置
  use: {
    // 基础 URL（支持环境变量）
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    
    // 浏览器上下文配置
    viewport: { width: 1920, height: 1080 },
    
    // 行动超时：15 秒
    actionTimeout: 15000,
    
    // 导航超时：30 秒
    navigationTimeout: 30000,
    
    // 请求超时：60 秒
    requestTimeout: 60000,
    
    // 仅在失败时收集追踪
    trace: 'on-first-retry',
    
    // 仅在失败时截图
    screenshot: 'only-on-failure',
    
    // 仅在失败时录制视频
    video: 'on-first-retry',
    
    // 存储状态（认证）
    storageState: 'playwright/.auth/storage-state.json',
  },
  
  // 文件夹配置
  outputDir: 'test-results/',
  snapshotDir: 'e2e/__snapshots__/',
  
  // 项目配置（多浏览器）
  projects: [
    // 认证项目 - 设置认证状态
    {
      name: 'setup',
      testMatch: /.*\.setup\.ts/,
    },
    
    // Chromium - 主要测试浏览器
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // 使用认证状态
        storageState: 'playwright/.auth/admin.json',
      },
      dependencies: ['setup'],
    },
    
    // Firefox - 跨浏览器测试
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        storageState: 'playwright/.auth/admin.json',
      },
      dependencies: ['setup'],
    },
    
    // WebKit - Safari 测试
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        storageState: 'playwright/.auth/admin.json',
      },
      dependencies: ['setup'],
    },
    
    // 移动端测试
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
      dependencies: ['setup'],
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
      dependencies: ['setup'],
    },
    
    // API 测试项目
    {
      name: 'api',
      testMatch: '**/api/**/*.spec.ts',
      testIgnore: '**/e2e/**/*.spec.ts',
    },
  ],
  
  // Web 服务器配置（用于本地开发测试）
  webServer: {
    command: process.env.CI ? undefined : 'npm run dev',
    url: process.env.BASE_URL || 'http://localhost:3000',
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI,
  },
});
