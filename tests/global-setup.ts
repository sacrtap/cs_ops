/**
 * Playwright Global Setup - 创建管理员认证状态
 * 
 * 运行方式：npx playwright test --global-setup=tests/global-setup.ts
 */
import { FullConfig } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

async function globalSetup(config: FullConfig) {
  console.log('🔧 创建管理员认证状态...');
  
  // 创建空的认证状态文件
  const authDir = path.join(process.cwd(), 'playwright/.auth');
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }
  
  // 创建管理员认证状态
  // 注意：这只是一个占位符，实际认证需要通过后端 API 获取
  const adminAuthState = {
    cookies: [],
    origins: [
      {
        origin: 'http://localhost:3000',
        localStorage: [
          {
            name: 'admin-auth',
            value: JSON.stringify({
              user_id: 'admin-user-id',
              email: 'admin@example.com',
              role: 'admin',
              username: 'admin',
            }),
          },
        ],
      },
    ],
  };
  
  fs.writeFileSync(
    path.join(authDir, 'admin.json'),
    JSON.stringify(adminAuthState, null, 2)
  );
  
  // 创建通用的 storage-state.json
  fs.writeFileSync(
    path.join(authDir, 'storage-state.json'),
    JSON.stringify(adminAuthState, null, 2)
  );
  
  console.log('✅ 管理员认证状态创建完成');
  console.log('📁 文件位置：playwright/.auth/admin.json');
}

export default globalSetup;
