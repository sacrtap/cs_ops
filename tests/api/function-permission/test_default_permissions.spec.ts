/**
 * 默认权限矩阵测试 - AC6
 *
 * 验证系统初始化时的默认权限配置
 */

import { test, expect } from "@playwright/test";

test.describe("Default Permissions - AC6", () => {
  test("should have admin all access", async ({ request }) => {
    // Given: 系统初始化
    // When: 获取 Admin 角色权限
    const response = await request.get("/api/v1/permission-matrix");
    const body = await response.json();

    // Then: Admin 拥有所有权限
    const adminPerms = body.data.admin;

    // 所有模块的所有操作都为 true
    expect(adminPerms.customer.read).toBe(true);
    expect(adminPerms.customer.create).toBe(true);
    expect(adminPerms.customer.update).toBe(true);
    expect(adminPerms.customer.delete).toBe(true);

    expect(adminPerms.settlement.read).toBe(true);
    expect(adminPerms.settlement.create).toBe(true);
    expect(adminPerms.settlement.update).toBe(true);
    expect(adminPerms.settlement.delete).toBe(true);

    expect(adminPerms.reporting.read).toBe(true);
    expect(adminPerms.reporting.create).toBe(true);
    expect(adminPerms.reporting.update).toBe(true);
    expect(adminPerms.reporting.delete).toBe(true);
  });

  test("should have manager most read and update", async ({ request }) => {
    // Given: 系统初始化
    // When: 获取经理角色权限
    const response = await request.get("/api/v1/permission-matrix");
    const body = await response.json();
    const managerPerms = body.data.manager;

    // Then: 经理有大部分 read 和 update 权限
    // 客户管理
    expect(managerPerms.customer.read).toBe(true);
    expect(managerPerms.customer.create).toBe(true);
    expect(managerPerms.customer.update).toBe(true);
    expect(managerPerms.customer.delete).toBe(false); // 不能删除

    // 结算管理
    expect(managerPerms.settlement.read).toBe(true);
    expect(managerPerms.settlement.create).toBe(false); // 不能创建
    expect(managerPerms.settlement.update).toBe(true);
    expect(managerPerms.settlement.delete).toBe(false); // 不能删除

    // 报表
    expect(managerPerms.reporting.read).toBe(true);
    expect(managerPerms.reporting.create).toBe(false);
    expect(managerPerms.reporting.update).toBe(false);
    expect(managerPerms.reporting.delete).toBe(false);
  });

  test("should have specialist most read create and update", async ({
    request,
  }) => {
    // Given: 系统初始化
    // When: 获取专员角色权限
    const response = await request.get("/api/v1/permission-matrix");
    const body = await response.json();
    const specialistPerms = body.data.specialist;

    // Then: 专员有大部分 read/create/update 权限
    // 客户管理
    expect(specialistPerms.customer.read).toBe(true);
    expect(specialistPerms.customer.create).toBe(true);
    expect(specialistPerms.customer.update).toBe(true);
    expect(specialistPerms.customer.delete).toBe(false); // 不能删除

    // 结算管理
    expect(specialistPerms.settlement.read).toBe(true);
    expect(specialistPerms.settlement.create).toBe(true);
    expect(specialistPerms.settlement.update).toBe(true);
    expect(specialistPerms.settlement.delete).toBe(false); // 不能删除

    // 报表
    expect(specialistPerms.reporting.read).toBe(true);
    expect(specialistPerms.reporting.create).toBe(false);
    expect(specialistPerms.reporting.update).toBe(false);
    expect(specialistPerms.reporting.delete).toBe(false);
  });

  test("should have sales customer read only", async ({ request }) => {
    // Given: 系统初始化
    // When: 获取销售角色权限
    const response = await request.get("/api/v1/permission-matrix");
    const body = await response.json();
    const salesPerms = body.data.sales;

    // Then: 销售只能读取客户数据
    // 客户管理 - 只能 read 和 update（更新自己的客户）
    expect(salesPerms.customer.read).toBe(true);
    expect(salesPerms.customer.create).toBe(false); // 不能创建
    expect(salesPerms.customer.update).toBe(true); // 可以更新自己的客户
    expect(salesPerms.customer.delete).toBe(false); // 不能删除

    // 结算管理 - 只能 read
    expect(salesPerms.settlement.read).toBe(true);
    expect(salesPerms.settlement.create).toBe(false);
    expect(salesPerms.settlement.update).toBe(false);
    expect(salesPerms.settlement.delete).toBe(false);

    // 报表 - 无权限
    expect(salesPerms.reporting.read).toBe(false);
    expect(salesPerms.reporting.create).toBe(false);
    expect(salesPerms.reporting.update).toBe(false);
    expect(salesPerms.reporting.delete).toBe(false);
  });

  test("should allow admin modify defaults", async ({ request }) => {
    // Given: Admin 用户登录
    const loginResponse = await request.post("/api/v1/auth/login", {
      data: {
        username: "admin",
        password: process.env.ADMIN_PASSWORD || "admin123",
      },
    });
    expect(loginResponse.status()).toBe(200);
    const authData = await loginResponse.json();

    // When: Admin 修改默认权限（给销售 reporting.read 权限）
    const updateResponse = await request.put("/api/v1/permission-matrix", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      data: {
        role: "sales",
        module: "reporting",
        action: "read",
        granted: true,
      },
    });

    expect(updateResponse.status()).toBe(200);

    // Then: 默认权限被修改
    const verifyResponse = await request.get("/api/v1/permission-matrix");
    const verifyBody = await verifyResponse.json();
    expect(verifyBody.data.sales.reporting.read).toBe(true);

    // And: Admin 可以恢复默认值
    await request.put("/api/v1/permission-matrix", {
      headers: {
        Authorization: `Bearer ${authData.data.token}`,
      },
      data: {
        role: "sales",
        module: "reporting",
        action: "read",
        granted: false,
      },
    });

    const finalResponse = await request.get("/api/v1/permission-matrix");
    const finalBody = await finalResponse.json();
    expect(finalBody.data.sales.reporting.read).toBe(false);
  });

  test("should seed default permissions on first run", async ({ request }) => {
    // Given: 权限表为空（首次运行）
    // When: 系统初始化或调用种子脚本
    const seedResponse = await request.post("/api/v1/permission-matrix/seed", {
      data: {
        reset: false, // 仅当表为空时播种
      },
    });

    // Then: 返回成功
    expect([200, 201]).toContain(seedResponse.status());

    // And: 默认权限被创建
    const verifyResponse = await request.get("/api/v1/permission-matrix");
    expect(verifyResponse.status()).toBe(200);
    const body = await verifyResponse.json();

    expect(body.data.admin).toBeDefined();
    expect(body.data.manager).toBeDefined();
    expect(body.data.specialist).toBeDefined();
    expect(body.data.sales).toBeDefined();
  });
});
