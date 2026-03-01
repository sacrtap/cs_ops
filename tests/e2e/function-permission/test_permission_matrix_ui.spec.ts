/**
 * 权限矩阵 UI 测试 - AC1, AC2
 *
 * 验证权限配置页面的功能
 */

import { test, expect } from "@playwright/test";

test.describe("Permission Matrix UI - AC1, AC2", () => {
  test.beforeEach(async ({ page }) => {
    // Setup: Admin 登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "admin");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.ADMIN_PASSWORD || "admin123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");
  });

  test("should display permission matrix page", async ({ page }) => {
    // Given: Admin 用户已登录
    // When: 导航到权限配置页面
    await page.goto("/admin/permission/matrix");

    // Then: 页面加载成功
    await expect(
      page.locator('[data-testid="permission-matrix-page"]'),
    ).toBeVisible();
    await expect(page).toHaveURL("/admin/permission/matrix");
  });

  test("should show all roles tabs", async ({ page }) => {
    // Given: Admin 在权限配置页面
    await page.goto("/admin/permission/matrix");

    // When: 查看角色标签页
    // Then: 显示所有 4 个角色标签页
    await expect(page.locator('[data-testid="role-tab-admin"]')).toBeVisible();
    await expect(
      page.locator('[data-testid="role-tab-manager"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="role-tab-specialist"]'),
    ).toBeVisible();
    await expect(page.locator('[data-testid="role-tab-sales"]')).toBeVisible();
  });

  test("should show all modules in matrix", async ({ page }) => {
    // Given: Admin 在权限配置页面
    await page.goto("/admin/permission/matrix");

    // When: 查看权限矩阵
    const matrixTable = page.locator('[data-testid="permission-matrix-table"]');
    await expect(matrixTable).toBeVisible();

    // Then: 显示所有功能模块
    await expect(
      page.locator('[data-testid="module-row-customer"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="module-row-settlement"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="module-row-reporting"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="module-row-permission"]'),
    ).toBeVisible();
  });

  test("should toggle permission checkbox", async ({ page }) => {
    // Given: Admin 在权限配置页面，查看销售角色
    await page.goto("/admin/permission/matrix");
    await page.click('[data-testid="role-tab-sales"]');

    // When: 切换 reporting.read 权限复选框
    const checkbox = page.locator(
      '[data-testid="permission-checkbox-sales-reporting-read"]',
    );
    const initialState = await checkbox.isChecked();
    await checkbox.click();

    // Then: 复选框状态改变
    await expect(checkbox).toBeChecked({ checked: !initialState });
  });

  test("should save permission changes", async ({ page }) => {
    // Given: Admin 修改了权限配置
    await page.goto("/admin/permission/matrix");
    await page.click('[data-testid="role-tab-sales"]');

    const checkbox = page.locator(
      '[data-testid="permission-checkbox-sales-reporting-read"]',
    );
    await checkbox.check();

    // When: 点击保存按钮
    await page.click('[data-testid="save-permission-btn"]');

    // Then: 保存成功
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText(
      "权限配置已保存",
    );
  });

  test("should show success message", async ({ page }) => {
    // Given: Admin 修改了权限配置
    await page.goto("/admin/permission/matrix");
    await page.click('[data-testid="role-tab-manager"]');

    const checkbox = page.locator(
      '[data-testid="permission-checkbox-manager-settlement-delete"]',
    );
    await checkbox.check();

    // When: 点击保存按钮
    await page.click('[data-testid="save-permission-btn"]');

    // Then: 显示成功提示
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toContainText(
      "保存成功",
    );

    // And: 提示在 3 秒后自动消失
    await page.waitForTimeout(3000);
    await expect(
      page.locator('[data-testid="success-message"]'),
    ).not.toBeVisible();
  });

  test("should warn before leaving with unsaved changes", async ({ page }) => {
    // Given: Admin 修改了权限配置但未保存
    await page.goto("/admin/permission/matrix");
    await page.click('[data-testid="role-tab-sales"]');
    await page
      .locator('[data-testid="permission-checkbox-sales-reporting-read"]')
      .check();

    // When: 尝试导航到其他页面
    // Then: 显示确认对话框（通过 browser event 验证）
    let confirmed = false;
    page.on("dialog", async (dialog) => {
      expect(dialog.message()).toContain("未保存的更改");
      confirmed = true;
      await dialog.accept();
    });

    await page.goto("/dashboard");
    expect(confirmed).toBe(true);
  });

  test("should highlight changed permissions", async ({ page }) => {
    // Given: Admin 在权限配置页面
    await page.goto("/admin/permission/matrix");
    await page.click('[data-testid="role-tab-sales"]');

    // When: 修改权限
    const checkbox = page.locator(
      '[data-testid="permission-checkbox-sales-reporting-read"]',
    );
    await checkbox.check();

    // Then: 复选框所在行被高亮显示
    await expect(checkbox).toHaveClass(/changed/);
  });
});
