/**
 * 路由权限守卫测试 - AC3
 *
 * 验证直接访问 URL 时的权限检查
 */

import { test, expect } from "@playwright/test";

test.describe("Route Permission Guard - AC3", () => {
  test("should allow admin access to all routes", async ({ page }) => {
    // Given: Admin 用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "admin");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.ADMIN_PASSWORD || "admin123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: Admin 访问客户管理路由
    await page.goto("/customers");
    await expect(page).toHaveURL("/customers");

    // And: Admin 访问结算管理路由
    await page.goto("/settlement");
    await expect(page).toHaveURL("/settlement");

    // And: Admin 访问报表路由
    await page.goto("/reporting");
    await expect(page).toHaveURL("/reporting");

    // And: Admin 访问权限配置路由
    await page.goto("/admin/permission/matrix");
    await expect(page).toHaveURL("/admin/permission/matrix");
  });

  test("should redirect sales to 403 on settlement route", async ({ page }) => {
    // Given: 销售用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "sales");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 销售尝试直接访问结算管理路由
    await page.goto("/settlement");

    // Then: 重定向到 403 页面
    await expect(page).toHaveURL("/403");
    await expect(page.locator('[data-testid="403-page"]')).toBeVisible();
    await expect(
      page.locator('[data-testid="permission-denied-message"]'),
    ).toContainText("没有权限访问此功能");
  });

  test("should redirect unauthenticated to login", async ({ page }) => {
    // Given: 未认证用户
    // When: 尝试访问受保护的路由
    await page.goto("/customers");

    // Then: 重定向到登录页面
    await expect(page).toHaveURL("/login");
    await expect(
      page.locator('input[data-testid="username-input"]'),
    ).toBeVisible();
  });

  test("should check permission on direct URL access", async ({ page }) => {
    // Given: 销售用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "sales");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 销售尝试直接访问权限配置路由
    await page.goto("/admin/permission/matrix");

    // Then: 重定向到 403 页面
    await expect(page).toHaveURL("/403");
  });

  test("should allow sales to access customer route", async ({ page }) => {
    // Given: 销售用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "sales");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 销售访问客户管理路由
    await page.goto("/customers");

    // Then: 允许访问
    await expect(page).toHaveURL("/customers");
  });

  test("should preserve return URL on 403 redirect", async ({ page }) => {
    // Given: 销售用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "sales");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 销售尝试访问结算管理路由
    await page.goto("/settlement");

    // Then: 重定向到 403，并显示返回按钮
    await expect(page).toHaveURL("/403");
    await expect(
      page.locator('[data-testid="back-to-home-btn"]'),
    ).toBeVisible();
  });

  test("should allow manager to access settlement route", async ({ page }) => {
    // Given: 经理用户登录
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "manager");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.USER_PASSWORD || "user123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 经理访问结算管理路由
    await page.goto("/settlement");

    // Then: 允许访问
    await expect(page).toHaveURL("/settlement");
  });

  test("should block access to non-existent route", async ({ page }) => {
    // Given: 已认证用户（任何角色）
    await page.goto("/login");
    await page.fill('input[data-testid="username-input"]', "admin");
    await page.fill(
      'input[data-testid="password-input"]',
      process.env.ADMIN_PASSWORD || "admin123",
    );
    await page.click('button[data-testid="login-btn"]');
    await page.waitForURL("/dashboard");

    // When: 访问不存在的路由
    await page.goto("/non-existent-route");

    // Then: 重定向到 404 页面
    await expect(page).toHaveURL("/404");
  });
});
