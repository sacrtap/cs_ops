/**
 * Playwright 测试 Fixtures - 内部运营中台客户信息管理与运营系统
 * 
 * 架构模式：
 * 1. 基础 fixture 扩展自 Playwright
 * 2. 自动清理钩子
 * 3. 数据工厂集成
 * 4. 认证会话管理
 */

import { test as base, expect } from '@playwright/test';
import { faker } from '@faker-js/faker';
import * as crypto from 'crypto';

// ===========================================
// 类型定义
// ===========================================

export interface CustomFixtures {
  // 测试数据
  testData: {
    user: UserInfo;
    customer: CustomerInfo;
  };
  
  // 自动清理
  cleanup: () => Promise<void>;
  
  // API 客户端
  apiClient: APIClient;
  
  // 认证
  authenticatedPage: {
    page: Page;
    userInfo: UserInfo;
  };
}

interface UserInfo {
  id: string;
  email: string;
  password: string;
  role: 'admin' | 'operator' | 'viewer';
}

interface CustomerInfo {
  id: string;
  name: string;
  email: string;
  phone: string;
}

interface APIClient {
  request: (options: {
    url: string;
    method?: string;
    data?: any;
    headers?: Record<string, string>;
  }) => Promise<any>;
  get: (url: string) => Promise<any>;
  post: (url: string, data: any) => Promise<any>;
  put: (url: string, data: any) => Promise<any>;
  delete: (url: string) => Promise<any>;
}

// ===========================================
// 数据工厂
// ===========================================

export class DataFactory {
  private static createdEntities: Array<{ type: string; id: string }> = [];
  
  static createUser(overrides?: Partial<UserInfo>): UserInfo {
    const user = {
      id: crypto.randomUUID(),
      email: faker.internet.email(),
      password: 'Test123456!',
      role: 'operator' as const,
      ...overrides,
    };
    
    this.createdEntities.push({ type: 'user', id: user.id });
    return user;
  }
  
  static createCustomer(overrides?: Partial<CustomerInfo>): CustomerInfo {
    const customer = {
      id: crypto.randomUUID(),
      name: faker.company.name(),
      email: faker.company.email(),
      phone: faker.phone.number(),
      ...overrides,
    };
    
    this.createdEntities.push({ type: 'customer', id: customer.id });
    return customer;
  }
  
  static async cleanup(): Promise<void> {
    // 在实际实现中，这里会调用 API 删除创建的数据
    console.log(`Cleanup: ${this.createdEntities.length} entities`);
    this.createdEntities = [];
  }
}

// ===========================================
// Fixtures 定义
// ===========================================

export const test = base.extend<CustomFixtures>({
  // 测试数据 fixture
  testData: async ({}, use) => {
    const testData = {
      user: DataFactory.createUser(),
      customer: DataFactory.createCustomer(),
    };
    
    await use(testData);
  },
  
  // 自动清理 fixture
  cleanup: async ({}, use) => {
    await use(() => Promise.resolve());
    
    // 测试后清理
    await DataFactory.cleanup();
  },
  
  // API 客户端 fixture
  apiClient: async ({ request }, use) => {
    const baseURL = process.env.TEST_API_URL || 'http://localhost:8000';
    
    const client: APIClient = {
      async request({ url, method = 'GET', data, headers }) {
        const response = await request.fetch(`${baseURL}${url}`, {
          method,
          data,
          headers: {
            'Content-Type': 'application/json',
            ...headers,
          },
        });
        return response.json();
      },
      
      async get(url) {
        return this.request({ url, method: 'GET' });
      },
      
      async post(url, data) {
        return this.request({ url, method: 'POST', data });
      },
      
      async put(url, data) {
        return this.request({ url, method: 'PUT', data });
      },
      
      async delete(url) {
        return this.request({ url, method: 'DELETE' });
      },
    };
    
    await use(client);
  },
  
  // 认证页面 fixture
  authenticatedPage: async ({ page, testData }, use) => {
    // 导航到登录页
    await page.goto('/login');
    
    // 使用测试用户登录
    await page.fill('[data-testid="email-input"]', testData.user.email);
    await page.fill('[data-testid="password-input"]', testData.user.password);
    await page.click('[data-testid="login-button"]');
    
    // 等待导航完成
    await page.waitForURL(/\/dashboard/);
    
    await use({
      page,
      userInfo: testData.user,
    });
    
    // 测试后登出（可选）
    // await page.click('[data-testid="logout-button"]');
  },
});

export { expect };
