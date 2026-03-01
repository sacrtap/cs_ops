/**
 * 权限中间件测试 - AC4
 *
 * 验证后端 API 权限验证中间件
 * 检查用户角色是否有该 API 的操作权限
 */

import { test, expect } from "@playwright/test";

test.describe("Permission Middleware - AC4", () => {
  test("should allow admin access to all APIs", async ({ request }) => {
    // Given: Admin 用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "admin",
        password: process.env.ADMIN_PASSWORD || "admin123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: Admin 访问受保护的 API
    const response = await request.get("/api/v1/settlement", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
    });

    // Then: 允许访问（200 或 404，但不是 403）
    expect([200, 404]).toContain(response.status());
  });

  test("should allow manager to read customer data", async ({ request }) => {
    // Given: 经理用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "manager",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 经理读取客户数据
    const response = await request.get("/api/v1/customers", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
    });

    // Then: 允许访问
    expect(response.status()).toBe(200);
  });

  test("should deny manager to create settlement", async ({ request }) => {
    // Given: 经理用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "manager",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 经理尝试创建结算
    const response = await request.post("/api/v1/settlement", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      data: {
        customer_id: 1,
        amount: 1000,
      },
    });

    // Then: 返回 403 禁止访问
    expect(response.status()).toBe(403);

    // And: 返回权限拒绝错误
    const body = await response.json();
    expect(body.error.code).toBe("PERMISSION_DENIED");
    expect(body.error.message).toContain("没有权限");
  });

  test("should allow sales to read customer data", async ({ request }) => {
    // Given: 销售用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "sales",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 销售读取客户数据
    const response = await request.get("/api/v1/customers", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
    });

    // Then: 允许访问
    expect(response.status()).toBe(200);
  });

  test("should deny sales to create customer", async ({ request }) => {
    // Given: 销售用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "sales",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 销售尝试创建客户
    const response = await request.post("/api/v1/customers", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      data: {
        name: "Test Customer",
        email: "test@example.com",
      },
    });

    // Then: 返回 403 禁止访问
    expect(response.status()).toBe(403);

    // And: 返回权限拒绝错误
    const body = await response.json();
    expect(body.error.code).toBe("PERMISSION_DENIED");
  });

  test("should deny sales to access settlement", async ({ request }) => {
    // Given: 销售用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "sales",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 销售尝试访问结算管理
    const response = await request.get("/api/v1/settlement", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
    });

    // Then: 返回 403 禁止访问
    expect(response.status()).toBe(403);
  });

  test("should return 403 with details", async ({ request }) => {
    // Given: 销售用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "sales",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 销售尝试访问无权限的 API
    const response = await request.post("/api/v1/settlement", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      data: {
        customer_id: 1,
        amount: 1000,
      },
    });

    // Then: 返回详细的权限拒绝信息
    expect(response.status()).toBe(403);
    const body = await response.json();
    expect(body.error.details).toBeDefined();
    expect(body.error.details.required_module).toBe("settlement");
    expect(body.error.details.required_action).toBe("create");
    expect(body.error.details.user_role).toBe("sales");
  });

  test("should log permission denied", async ({ request }) => {
    // Given: 销售用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "sales",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 销售尝试访问无权限的 API
    await request.post("/api/v1/settlement", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      data: {
        customer_id: 1,
        amount: 1000,
      },
    });

    // Then: 审计日志被记录
    const auditResponse = await request.get("/api/v1/audit-logs", {
      params: {
        event_type: "permission_denied",
        limit: "1",
      },
    });

    expect(auditResponse.status()).toBe(200);
    const body = await auditResponse.json();
    expect(body.data.length).toBeGreaterThan(0);

    const log = body.data[0];
    expect(log.event_type).toBe("permission_denied");
    expect(log.user_id).toBeDefined();
    expect(log.resource).toBe("settlement");
    expect(log.action).toBe("create");
  });
});
