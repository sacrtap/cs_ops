/**
 * 权限矩阵结构测试 - AC1
 *
 * 验证权限矩阵 API 返回正确的数据结构
 * 包含所有角色、模块和操作权限
 */

import { test, expect } from "@playwright/test";
import { APIRequestContext } from "playwright-core";

// 测试数据
const ROLES = ["admin", "manager", "specialist", "sales"];
const MODULES = ["customer", "settlement", "reporting", "permission"];
const ACTIONS = ["read", "create", "update", "delete"];

test.describe("Permission Matrix Structure - AC1", () => {
  let context: APIRequestContext;

  test.beforeAll(async ({ request }) => {
    context = await request.newContext({
      baseURL: process.env.BASE_URL || "http://localhost:8000",
    });
  });

  test.afterAll(async () => {
    await context.dispose();
  });

  test("should get permission matrix structure", async () => {
    // Given: 权限矩阵 API 可用
    // When: GET 请求权限矩阵接口
    const response = await context.get("/api/v1/permission-matrix");

    // Then: 返回 200 状态码
    expect(response.status()).toBe(200);

    // And: 响应结构正确
    const body = await response.json();
    expect(body).toHaveProperty("data");
    expect(body).toHaveProperty("meta");
    expect(body.meta).toHaveProperty("timestamp");
    expect(body.meta).toHaveProperty("request_id");
  });

  test("should have all roles", async () => {
    // Given: 权限矩阵包含所有角色
    // When: 获取权限矩阵
    const response = await context.get("/api/v1/permission-matrix");
    const body = await response.json();

    // Then: 包含所有 4 个角色
    const data = body.data;
    ROLES.forEach((role) => {
      expect(data).toHaveProperty(role);
    });

    // And: 角色数量为 4
    expect(Object.keys(data).length).toBe(4);
  });

  test("should have all modules for each role", async () => {
    // Given: 每个角色都有所有功能模块
    // When: 获取权限矩阵
    const response = await context.get("/api/v1/permission-matrix");
    const body = await response.json();

    // Then: 每个角色包含所有模块
    const data = body.data;
    Object.keys(data).forEach((role) => {
      MODULES.forEach((module) => {
        expect(data[role]).toHaveProperty(module);
      });
    });
  });

  test("should have all actions for each module", async () => {
    // Given: 每个模块都有 4 级操作权限
    // When: 获取权限矩阵
    const response = await context.get("/api/v1/permission-matrix");
    const body = await response.json();

    // Then: 每个模块包含 read/create/update/delete
    const data = body.data;
    Object.keys(data).forEach((role) => {
      MODULES.forEach((module) => {
        ACTIONS.forEach((action) => {
          expect(data[role][module]).toHaveProperty(action);
          expect(typeof data[role][module][action]).toBe("boolean");
        });
      });
    });
  });

  test("should return admin with all permissions granted", async () => {
    // Given: Admin 角色拥有所有权限
    // When: 获取权限矩阵
    const response = await context.get("/api/v1/permission-matrix");
    const body = await response.json();

    // Then: Admin 的所有权限都为 true
    const adminPerms = body.data.admin;
    MODULES.forEach((module) => {
      ACTIONS.forEach((action) => {
        expect(adminPerms[module][action]).toBe(true);
      });
    });
  });

  test("should have valid permission values (boolean only)", async () => {
    // Given: 权限值只能是 boolean
    // When: 获取权限矩阵
    const response = await context.get("/api/v1/permission-matrix");
    const body = await response.json();

    // Then: 所有权限值都是 boolean 类型
    const data = body.data;
    Object.keys(data).forEach((role) => {
      MODULES.forEach((module) => {
        ACTIONS.forEach((action) => {
          const value = data[role][module][action];
          expect(typeof value).toBe("boolean");
          expect([true, false]).toContain(value);
        });
      });
    });
  });
});
