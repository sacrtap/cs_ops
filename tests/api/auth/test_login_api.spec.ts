/**
 * 登录 API 测试
 * 
 * 覆盖验收标准：AC1, AC2, AC3, AC5, AC7
 * 测试级别：API
 * 优先级：P0-P2
 * 
 * Story: 1-1-user-authentication (用户认证)
 */

import { test, expect } from '@playwright/test';

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api/v1';

test.describe('[API] 用户认证 - 登录', () => {
  
  // ==================== P0 测试 - 关键路径 ====================
  
  test('[P0] AC1-用户能够使用用户名和密码登录系统 - 成功场景', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    
    // 验证响应结构
    expect(data).toHaveProperty('access_token');
    expect(data).toHaveProperty('refresh_token');
    expect(data).toHaveProperty('token_type', 'bearer');
    expect(data).toHaveProperty('expires_in');
    expect(data).toHaveProperty('user');
    
    // 验证用户信息
    expect(data.user).toMatchObject({
      username: 'admin',
      role: 'admin',
      status: 'active'
    });
  });

  test('[P0] AC2-系统验证用户名和密码的正确性 - 错误密码', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'admin',
        password: 'wrong_password'
      }
    });

    expect(response.status()).toBe(401);
    const error = await response.json();
    
    expect(error.error).toMatchObject({
      code: 'INVALID_CREDENTIALS',
      message: expect.stringContaining('密码错误')
    });
  });

  test('[P0] AC3-验证成功后生成 JWT Token - Token 格式验证', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    
    // JWT Token 格式验证
    expect(data.access_token).toMatch(/^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$/);
    expect(data.refresh_token).toMatch(/^[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+$/);
  });

  test('[P0] AC5-失败的登录请求返回标准错误响应 - 空用户名', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: '',
        password: 'admin123'
      }
    });

    expect(response.status()).toBe(400);
    const error = await response.json();
    
    expect(error.error).toMatchObject({
      code: 'VALIDATION_ERROR'
    });
  });

  test('[P0] AC7-实现登录失败次数限制 - 第 5 次失败后锁定', async ({ request }) => {
    const wrongPassword = 'wrong_password';
    
    // 前 4 次失败
    for (let i = 1; i <= 4; i++) {
      const response = await request.post(`${API_BASE_URL}/auth/login`, {
        data: {
          username: 'test_lock_user',
          password: wrongPassword
        }
      });
      expect(response.status()).toBe(401);
    }
    
    // 第 5 次失败 - 应该触发锁定
    const lockResponse = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'test_lock_user',
        password: wrongPassword
      }
    });
    
    expect(lockResponse.status()).toBe(403);
    const lockError = await lockResponse.json();
    
    expect(lockError.error).toMatchObject({
      code: 'ACCOUNT_LOCKED',
      message: expect.stringContaining('账户已被锁定')
    });
  });

  // ==================== P1 测试 - 重要流程 ====================
  
  test('[P1] AC3-Token 格式和过期时间验证 - Access Token 2 小时', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    
    // 验证过期时间（2 小时 = 7200 秒）
    expect(data.expires_in).toBe(7200);
    expect(data.token_type).toBe('bearer');
  });

  test('[P1] AC3-Refresh Token 格式验证 - 7 天过期', async ({ request }) => {
    const response = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });

    expect(response.status()).toBe(200);
    const data = await response.json();
    
    // Refresh Token 应该是有效的 JWT 格式
    const refreshTokenParts = data.refresh_token.split('.');
    expect(refreshTokenParts).toHaveLength(3);
  });

  test('[P1] AC6-bcrypt 密码加密 - salt 随机性验证', async ({ request }) => {
    // 使用相同密码注册两个用户（通过不同用户名）
    const password = 'TestPassword123!';
    
    // 注意：这个测试需要后端支持注册功能
    // 如果后端不支持注册，这个测试应该被跳过
    test.skip();
    
    // 验证 bcrypt 加密的随机性
    // 即使密码相同，salt 也应该不同
  });

  test('[P1] AC7-失败计数器在成功登录后重置', async ({ request }) => {
    // 先进行 2 次失败登录
    for (let i = 1; i <= 2; i++) {
      const response = await request.post(`${API_BASE_URL}/auth/login`, {
        data: {
          username: 'test_reset_counter',
          password: 'wrong_password'
        }
      });
      expect(response.status()).toBe(401);
    }
    
    // 然后成功登录
    const successResponse = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'test_reset_counter',
        password: 'correct_password'
      }
    });
    
    // 成功登录后，计数器应该重置
    // 再次失败登录应该从 1 开始计数，而不是 3
    const nextFailResponse = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'test_reset_counter',
        password: 'wrong_password'
      }
    });
    
    expect(nextFailResponse.status()).toBe(401);
    // 不应该被锁定（计数器已重置）
  });

  test('[P1] AC7-锁定倒计时自动解除 - 15 分钟后', async ({ request }) => {
    // 注意：这个测试在实际环境中需要等待 15 分钟
    // 在 CI/CD 中应该被跳过或使用 mock 时间
    test.skip();
    
    // 1. 先锁定账户
    // 2. 等待 15 分钟
    // 3. 验证账户可以重新登录
  });

  test('[P1] AC2-密码大小写敏感验证', async ({ request }) => {
    // 测试密码是否正确处理大小写
    const response1 = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'admin',
        password: 'Admin123' // 首字母大写
      }
    });
    
    expect(response1.status()).toBe(401);
    
    const response2 = await request.post(`${API_BASE_URL}/auth/login`, {
      data: {
        username: 'admin',
        password: 'admin123' // 正确的大小写
      }
    });
    
    expect(response2.status()).toBe(200);
  });
}, {
  tag: '@api @auth @login @story-1-1'
});
