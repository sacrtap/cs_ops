/**
 * 权限更新测试 - AC2
 *
 * 验证权限配置的保存、验证和立即生效
 */

import { test, expect } from "@playwright/test";

test.describe("Update Permissions - AC2", () => {
  test.beforeEach(async ({ request }) => {
    // Setup: 创建测试用户和认证
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "admin",
        password: process.env.ADMIN_PASSWORD || "admin123",
      },
    });

    const authData = await loginResponse.json();
    expect(loginResponse.status()).toBe(200);

    // 存储认证 token 用于后续请求
    await request.storageState({
      cookies: [],
      origins: [
        {
          origin: process.env.BASE_URL || "http://localhost:8000",
          localStorage: [{ name: "auth_token", value: authData.data.token }],
        },
      ],
    });
  });

  test("should update single permission", async ({ request }) => {
    // Given: 销售角色默认没有 reporting.read 权限
    // When: Admin 更新销售角色的 reporting.read 权限为 true
    const response = await request.put("/api/v1/permission-matrix", {
      data: {
        role: "sales",
        module: "reporting",
        action: "read",
        granted: true,
      },
    });

    // Then: 返回 200 状态码
    expect(response.status()).toBe(200);

    // And: 返回成功消息
    const body = await response.json();
    expect(body.data.success).toBe(true);

    // And: 权限实际被更新
    const verifyResponse = await request.get("/api/v1/permission-matrix");
    const verifyBody = await verifyResponse.json();
    expect(verifyBody.data.sales.reporting.read).toBe(true);
  });

  test("should bulk update permissions", async ({ request }) => {
    // Given: 多个权限需要更新
    const permissions = [
      { role: "sales", module: "reporting", action: "read", granted: true },
      { role: "sales", module: "settlement", action: "read", granted: true },
      {
        role: "manager",
        module: "settlement",
        action: "delete",
        granted: true,
      },
    ];

    // When: 批量更新权限
    const response = await request.put("/api/v1/permission-matrix/bulk", {
      data: { permissions },
    });

    // Then: 返回 200 状态码
    expect(response.status()).toBe(200);

    // And: 所有权限都被更新
    const verifyResponse = await request.get("/api/v1/permission-matrix");
    const verifyBody = await verifyResponse.json();

    expect(verifyBody.data.sales.reporting.read).toBe(true);
    expect(verifyBody.data.sales.settlement.read).toBe(true);
    expect(verifyBody.data.manager.settlement.delete).toBe(true);
  });

  test("should validate permission integrity", async ({ request }) => {
    // Given: 尝试删除角色的所有权限
    const permissions = [
      { role: "sales", module: "customer", action: "read", granted: false },
      { role: "sales", module: "customer", action: "create", granted: false },
      { role: "sales", module: "customer", action: "update", granted: false },
      { role: "sales", module: "customer", action: "delete", granted: false },
      { role: "sales", module: "settlement", action: "read", granted: false },
      // ... 所有权限都设置为 false
    ];

    // When: 尝试保存
    const response = await request.put("/api/v1/permission-matrix/bulk", {
      data: { permissions },
    });

    // Then: 返回 400 错误（每个角色至少需要一个权限）
    expect(response.status()).toBe(400);

    // And: 返回验证错误消息
    const body = await response.json();
    expect(body.error).toBeDefined();
    expect(body.error.code).toBe("VALIDATION_ERROR");
    expect(body.error.message).toContain("至少一个功能权限");
  });

  test("should record audit log", async ({ request }) => {
    // Given: 权限更新操作
    // When: 更新权限
    await request.put("/api/v1/permission-matrix", {
      data: {
        role: "sales",
        module: "reporting",
        action: "read",
        granted: true,
      },
    });

    // Then: 审计日志被记录
    const auditResponse = await request.get("/api/v1/audit-logs", {
      params: {
        action: "permission_updated",
        limit: "1",
      },
    });

    expect(auditResponse.status()).toBe(200);
    const body = await auditResponse.json();
    expect(body.data.length).toBeGreaterThan(0);

    const log = body.data[0];
    expect(log.action).toBe("permission_updated");
    expect(log.changes).toBeDefined();
    expect(log.changed_by).toBeDefined();
  });

  test("should return 400 for invalid role", async ({ request }) => {
    // Given: 无效的角色名称
    // When: 尝试更新权限
    const response = await request.put("/api/v1/permission-matrix", {
      data: {
        role: "invalid_role",
        module: "customer",
        action: "read",
        granted: true,
      },
    });

    // Then: 返回 400 错误
    expect(response.status()).toBe(400);

    // And: 返回验证错误
    const body = await response.json();
    expect(body.error).toBeDefined();
    expect(body.error.code).toBe("VALIDATION_ERROR");
    expect(body.error.message).toContain("无效的角色");
  });

  test("should return 400 for invalid module", async ({ request }) => {
    // Given: 无效的模块名称
    // When: 尝试更新权限
    const response = await request.put("/api/v1/permission-matrix", {
      data: {
        role: "sales",
        module: "invalid_module",
        action: "read",
        granted: true,
      },
    });

    // Then: 返回 400 错误
    expect(response.status()).toBe(400);

    // And: 返回验证错误
    const body = await response.json();
    expect(body.error).toBeDefined();
    expect(body.error.code).toBe("VALIDATION_ERROR");
    expect(body.error.message).toContain("无效的模块");
  });

  test("should return 403 for non-admin user", async ({ request }) => {
    // Given: 非 Admin 用户（销售角色）
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "sales_user",
        password: process.env.USER_PASSWORD || "user123",
      },
    });

    expect(loginResponse.status()).toBe(200);

    // When: 尝试更新权限
    const response = await request.put("/api/v1/permission-matrix", {
      data: {
        role: "sales",
        module: "reporting",
        action: "read",
        granted: true,
      },
    });

    // Then: 返回 403 错误（只有 Admin 可以修改权限）
    expect(response.status()).toBe(403);

    // And: 返回权限拒绝错误
    const body = await response.json();
    expect(body.error).toBeDefined();
    expect(body.error.code).toBe("PERMISSION_DENIED");
    expect(body.error.message).toContain("没有权限");
  });
});
