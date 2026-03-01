/**
 * 权限缓存测试 - AC5
 *
 * 验证权限矩阵的 LRU 缓存机制
 * 缓存 30 分钟过期，更新后清除缓存
 */

import { test, expect } from "@playwright/test";

test.describe("Permission Cache - AC5", () => {
  test("should cache permission query", async ({ request }) => {
    // Given: 用户首次请求权限
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "sales",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 第一次检查权限（应该查询数据库）
    const response1 = await request.get("/api/v1/permission-matrix/check", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      params: {
        module: "customer",
        action: "read",
      },
    });

    expect(response1.status()).toBe(200);
    const body1 = await response1.json();
    expect(body1.data.granted).toBe(true);
    expect(body1.meta.cache_hit).toBe(false); // 第一次应该是 cache miss

    // And: 第二次检查权限（应该使用缓存）
    const response2 = await request.get("/api/v1/permission-matrix/check", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      params: {
        module: "customer",
        action: "read",
      },
    });

    expect(response2.status()).toBe(200);
    const body2 = await response2.json();
    expect(body2.data.granted).toBe(true);
    expect(body2.meta.cache_hit).toBe(true); // 第二次应该是 cache hit
  });

  test("should use cache on second request", async ({ request }) => {
    // Given: 已登录用户
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "manager",
        password: process.env.USER_PASSWORD || "user123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: 连续两次请求相同权限检查
    await request.get("/api/v1/permission-matrix/check", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      params: {
        module: "settlement",
        action: "read",
      },
    });

    const response2 = await request.get("/api/v1/permission-matrix/check", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      params: {
        module: "settlement",
        action: "read",
      },
    });

    // Then: 第二次使用缓存
    const body2 = await response2.json();
    expect(body2.meta.cache_hit).toBe(true);
    expect(body2.meta.cache_key).toBeDefined();
  });

  test("should clear cache on permission update", async ({ request }) => {
    // Given: Admin 用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "admin",
        password: process.env.ADMIN_PASSWORD || "admin123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // And: Admin 首次检查权限（缓存）
    const checkResponse1 = await request.get(
      "/api/v1/permission-matrix/check",
      {
        headers: {
          Authorization: `Bearer ${authData.data.token}`,
        },
        params: {
          module: "reporting",
          action: "read",
        },
      },
    );
    expect(checkResponse1.status()).toBe(200);
    const checkBody1 = await checkResponse1.json();
    expect(checkBody1.data.granted).toBe(true);

    // When: Admin 更新销售角色的 reporting.read 权限
    await request.put("/api/v1/permission-matrix", {
      data: {
        role: "sales",
        module: "reporting",
        action: "read",
        granted: true,
      },
    });

    // And: 销售用户再次检查权限
    const checkResponse2 = await request.get(
      "/api/v1/permission-matrix/check",
      {
        headers: {
          Authorization: `Bearer ${authData.data.token}`,
        },
        params: {
          module: "reporting",
          action: "read",
        },
      },
    );

    // Then: 缓存被清除，重新查询数据库
    const body2 = await checkResponse2.json();
    expect(body2.meta.cache_hit).toBe(false); // cache miss，因为缓存被清除
    expect(body2.data.granted).toBe(true); // 新权限生效
  });

  test("should return cache statistics", async ({ request }) => {
    // Given: Admin 用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "admin",
        password: process.env.ADMIN_PASSWORD || "admin123",
      },
    });
    expect(loginResponse.status()).toBe(200);

    // When: 请求缓存统计
    const response = await request.get(
      "/api/v1/permission-matrix/cache/stats",
      {
        headers: {
          Authorization: `Bearer ${authData.data.token}`,
        },
      },
    );

    // Then: 返回缓存统计信息
    expect(response.status()).toBe(200);
    const body = await response.json();
    expect(body.data).toHaveProperty("size");
    expect(body.data).toHaveProperty("hits");
    expect(body.data).toHaveProperty("misses");
    expect(body.data).toHaveProperty("hit_rate");
    expect(body.data.max_size).toBe(128); // LRU cache max size
    expect(body.data.ttl_seconds).toBe(1800); // 30 minutes
  });
});
