/**
 * 菜单权限过滤测试 - AC3
 *
 * 验证主菜单根据用户角色过滤无权限项目
 */

import { test, expect } from "@playwright/test";

test.describe("Menu Permission Filter - AC3", () => {
  test("should show all menus for admin", async ({ page }) => {
    // Given: Admin 用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "admin");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.ADMIN_PASSWORD || "admin123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 查看主菜单
    const mainMenu = page.locator('[data-testid="main-menu"]');
    await expect(mainMenu).toBeVisible();

    // Then: Admin 看到所有菜单项
    await expect(
      page.locator('[data-testid="menu-item-customer"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="menu-item-settlement"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="menu-item-reporting"]'),
    ).toBeVisible();
    await expect(
      page.locator('[data-testid="menu-item-permission"]'),
    ).toBeVisible();
  });

  test("should hide settlement menu for sales", async ({ page }) => {
    // Given: 销售用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "sales");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 查看主菜单
    const mainMenu = page.locator('[data-testid="main-menu"]');
    await expect(mainMenu).toBeVisible();

    // Then: 销售看到客户管理菜单
    await expect(
      page.locator('[data-testid="menu-item-customer"]'),
    ).toBeVisible();

    // And: 销售看不到结算管理菜单（或显示灰色不可点击）
    const settlementMenu = page.locator('[data-testid="menu-item-settlement"]');
    await expect(settlementMenu).not.toBeVisible();
  });

  test("should grey out no access items", async ({ page }) => {
    // Given: 销售用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "sales");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 查看主菜单
    const reportingMenu = page.locator('[data-testid="menu-item-reporting"]');

    // Then: 报表菜单显示为灰色（无权限）
    await expect(reportingMenu).toHaveClass(/disabled|greyed-out/);
    await expect(reportingMenu).not.toBeEnabled();
  });

  test("should refresh menu on permission change", async ({ page }) => {
    // Given: Admin 用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "admin");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.ADMIN_PASSWORD || "admin123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: Admin 修改销售角色的 reporting.read 权限
    await page.goto("/admin/permission/matrix");
    await page.click('[data-testid="role-tab-sales"]');
    await page
      .locator('[data-testid="permission-checkbox-sales-reporting-read"]')
      .check();
    await page.click('[data-testid="save-permission-btn"]');
    await page.waitForTimeout(1000); // 等待权限更新生效

    // And: 切换到销售用户
    await page.click('[data-testid="logout-btn"]');
    await page.waitForURL("/login");

    await page.fill('input[data-testid="username-input"]', "sales");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // Then: 销售现在可以看到报表菜单
    await expect(
      page.locator('[data-testid="menu-item-reporting"]'),
    ).toBeVisible();
  });

  test("should show manager limited menus", async ({ page }) => {
    // Given: 经理用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "manager");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 查看主菜单
    const mainMenu = page.locator('[data-testid="main-menu"]');
    await expect(mainMenu).toBeVisible();

    // Then: 经理看到客户管理菜单
    await expect(
      page.locator('[data-testid="menu-item-customer"]'),
    ).toBeVisible();

    // And: 经理看到结算管理菜单
    await expect(
      page.locator('[data-testid="menu-item-settlement"]'),
    ).toBeVisible();

    // And: 经理看到报表菜单（只读）
    await expect(
      page.locator('[data-testid="menu-item-reporting"]'),
    ).toBeVisible();
  });

  test("should highlight active menu item", async ({ page }) => {
    // Given: Admin 用户登录并进入客户管理页面
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "admin");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.ADMIN_PASSWORD || "admin123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/customers");

    // When: 查看主菜单
    // Then: 客户管理菜单项高亮显示
    const customerMenuItem = page.locator('[data-testid="menu-item-customer"]');
    await expect(customerMenuItem).toHaveClass(/active/);
  });
});
