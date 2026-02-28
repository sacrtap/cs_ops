/**
 * 用户登录 E2E 测试 - ATDD (TDD Red Phase)
 *
 * Story: 1-1-user-authentication
 * Epic: 1 - 权限与认证
 * Generated: 2026-02-27
 * TDD Phase: RED (tests will fail until feature implemented)
 *
 * P0 验收标准覆盖:
 * 1. 用户能够使用用户名和密码登录系统
 * 2. 系统验证用户名和密码的正确性
 * 3. Token 返回给前端并存储在 localStorage + Pinia Store
 * 4. 失败的登录请求返回标准错误响应
 * 5. 表单验证（用户名/密码不能为空）
 */

import { test, expect } from "../../support/fixtures";
import { DataFactory } from "../../support/fixtures/index";

test.describe("用户登录 E2E 测试 - P0 场景", () => {
  test.beforeEach(async ({ page }) => {
    // Given: 访问登录页面
    await page.goto("/login");

    // Then: 应该显示登录表单
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  // ===========================================
  // AC1: 用户能够使用用户名和密码登录系统
  // ===========================================

  test.skip("P0-AC1-01 - 应该成功登录并跳转到首页", async ({
    page,
    testData,
  }) => {
    // Given: 已注册的有效用户
    const userInfo = testData.user;

    // When: 输入有效的用户名和密码
    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', userInfo.password);

    // When: 点击登录按钮
    await page.click('[data-testid="login-button"]');

    // Then: 应该跳转到首页（dashboard）
    await expect(page).toHaveURL(/\/dashboard/);

    // Then: 应该显示欢迎信息
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  });

  test.skip("P0-AC1-02 - 应该支持记住登录状态（刷新页面保持登录）", async ({
    page,
    testData,
  }) => {
    // Given: 已登录的用户
    const userInfo = testData.user;
    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', userInfo.password);
    await page.click('[data-testid="login-button"]');
    await page.waitForURL(/\/dashboard/);

    // When: 刷新页面
    await page.reload();

    // Then: 应该保持登录状态，仍在 dashboard 页面
    await expect(page).toHaveURL(/\/dashboard/);

    // Then: 应该仍然显示欢迎信息
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  });

  // ===========================================
  // AC2: 系统验证用户名和密码的正确性
  // ===========================================

  test.skip("P0-AC2-01 - 应该拒绝错误的密码", async ({ page, testData }) => {
    // Given: 有效的用户名但错误的密码
    const userInfo = testData.user;
    const wrongPassword = "WrongPassword123!";

    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', wrongPassword);

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示错误提示
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText(
      /用户名或密码错误/,
    );

    // Then: 应该停留在登录页
    await expect(page).toHaveURL(/\/login/);
  });

  test.skip("P0-AC2-02 - 应该拒绝不存在的用户名", async ({ page }) => {
    // Given: 不存在的用户名
    const nonExistentEmail = "nonexistent@example.com";
    const password = "Test123456!";

    await page.fill('[data-testid="username-input"]', nonExistentEmail);
    await page.fill('[data-testid="password-input"]', password);

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示错误提示（不透露用户是否存在）
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText(
      /用户名或密码错误/,
    );

    // Then: 应该停留在登录页
    await expect(page).toHaveURL(/\/login/);
  });

  test.skip("P0-AC2-03 - 应该区分大小写验证用户名", async ({
    page,
    testData,
  }) => {
    // Given: 有效用户但用户名大小写不匹配
    const userInfo = testData.user;
    const wrongCaseEmail = userInfo.email.toUpperCase();

    await page.fill('[data-testid="username-input"]', wrongCaseEmail);
    await page.fill('[data-testid="password-input"]', userInfo.password);

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示错误提示
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText(
      /用户名或密码错误/,
    );
  });

  // ===========================================
  // AC4: Token 返回给前端并存储在 localStorage + Pinia Store
  // ===========================================

  test('[P1] AC4-01 - Token 应该存储在 localStorage 和 Pinia Store', async ({
    page,
    testData,
  }) => {
    const userInfo = testData.user;

    // When: 成功登录
    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', userInfo.password);
    await page.click('[data-testid="login-button"]');

    await expect(page).toHaveURL(/\/dashboard/);

    // Then: localStorage 应该包含 Token
    const accessToken = await page.evaluate(() =>
      localStorage.getItem('access_token')
    );
    const refreshToken = await page.evaluate(() =>
      localStorage.getItem('refresh_token')
    );

    expect(accessToken).toBeTruthy();
    expect(refreshToken).toBeTruthy();

    // Then: Pinia Store 也应该有 Token（通过检查页面行为）
    // 注意：直接访问 Pinia Store 需要通过 window 对象
    const authState = await page.evaluate(() => {
      const state = (window as any).__PINIA_STORE_AUTH__;
      return state;
    });

    expect(authState).toMatchObject({
      isAuthenticated: true,
      user: expect.objectContaining({
        username: userInfo.username,
      }),
    });
  });

  test('[P1] AC3-02 - Token 自动刷新功能验证', async ({ page, testData }) => {
    const userInfo = testData.user;

    // Given: 用户已登录
    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', userInfo.password);
    await page.click('[data-testid="login-button"]');

    await expect(page).toHaveURL(/\/dashboard/);

    // Note: 完整的 Token 刷新测试需要 mock 时间或等待 Token 过期
    // 这里测试 Token 刷新机制是否存在
    
    // 检查是否有刷新 Token 的逻辑（通过拦截请求）
    let refreshRequest = false;
    
    page.on('request', (request) => {
      if (request.url().includes('/auth/refresh')) {
        refreshRequest = true;
      }
    });

    // 模拟 Token 过期的场景（需要后端支持 mock）
    // 在实际 E2E 测试中，这可能需要使用 playright 的 time 功能
    test.skip();
  });

  test.skip("P0-AC3-01 - 应该成功获取并存储访问令牌", async ({
    page,
    testData,
  }) => {
    // Given: 有效的登录凭据
    const userInfo = testData.user;
    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', userInfo.password);

    // When: 登录成功
    await page.click('[data-testid="login-button"]');
    await page.waitForURL(/\/dashboard/);

    // Then: localStorage 应该包含 token
    const localStorageToken = await page.evaluate(() => {
      return localStorage.getItem("access_token");
    });
    expect(localStorageToken).toBeTruthy();
    expect(localStorageToken!.length).toBeGreaterThan(0);
  });

  test.skip("P0-AC3-02 - 应该存储刷新令牌", async ({ page, testData }) => {
    // Given: 有效的登录凭据
    const userInfo = testData.user;
    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', userInfo.password);

    // When: 登录成功
    await page.click('[data-testid="login-button"]');
    await page.waitForURL(/\/dashboard/);

    // Then: localStorage 应该包含 refresh token
    const refreshToken = await page.evaluate(() => {
      return localStorage.getItem("refresh_token");
    });
    expect(refreshToken).toBeTruthy();
    expect(refreshToken!.length).toBeGreaterThan(0);
  });

  test.skip("P0-AC3-03 - 应该在 Pinia Store 中存储用户信息", async ({
    page,
    testData,
  }) => {
    // Given: 有效的登录凭据
    const userInfo = testData.user;
    await page.fill('[data-testid="username-input"]', userInfo.email);
    await page.fill('[data-testid="password-input"]', userInfo.password);

    // When: 登录成功
    await page.click('[data-testid="login-button"]');
    await page.waitForURL(/\/dashboard/);

    // Then: Pinia Store 应该包含用户信息
    const storeUser = await page.evaluate(() => {
      // 假设 Pinia store 挂载在 window 上
      const store = (window as any).__pinia?.state?.value?.auth;
      return store?.user;
    });

    expect(storeUser).toBeTruthy();
    expect(storeUser?.email).toBe(userInfo.email);
  });

  // ===========================================
  // AC4: 失败的登录请求返回标准错误响应
  // ===========================================

  test.skip("P0-AC4-01 - 应该返回标准错误格式", async ({ page }) => {
    // Given: 无效的登录凭据
    await page.fill('[data-testid="username-input"]', "wrong@example.com");
    await page.fill('[data-testid="password-input"]', "WrongPassword123!");

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 错误响应应该包含标准字段
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-code"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
  });

  test.skip("P0-AC4-02 - 应该隐藏详细的错误信息（安全）", async ({ page }) => {
    // Given: 尝试使用不存在的用户登录
    await page.fill(
      '[data-testid="username-input"]',
      "nonexistent@example.com",
    );
    await page.fill('[data-testid="password-input"]', "SomePassword123!");

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 错误信息不应该透露用户是否存在
    const errorMessage = await page
      .locator('[data-testid="login-error"]')
      .textContent();
    expect(errorMessage).not.toContain("用户不存在");
    expect(errorMessage).not.toContain("user not found");
    expect(errorMessage).not.toContain("404");
  });

  test.skip("P0-AC4-03 - 应该在网络错误时显示友好提示", async ({ page }) => {
    // Given: 模拟网络错误
    await page.route("**/api/auth/login", async (route) => {
      await route.abort("failed");
    });

    await page.fill('[data-testid="username-input"]', "test@example.com");
    await page.fill('[data-testid="password-input"]', "Test123456!");

    // When: 尝试登录（网络失败）
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示友好的网络错误提示
    await expect(page.locator('[data-testid="network-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="network-error"]')).toContainText(
      /网络连接失败|服务器无响应|请稍后重试/,
    );
  });

  // ===========================================
  // AC5: 表单验证（用户名/密码不能为空）
  // ===========================================

  test.skip("P0-AC5-01 - 应该验证用户名不能为空", async ({ page }) => {
    // Given: 用户名为空
    await page.fill('[data-testid="password-input"]', "Test123456!");

    // When: 尝试提交表单
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示用户名验证错误
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="username-error"]')).toContainText(
      /用户名不能为空|请输入用户名/,
    );

    // Then: 不应该发送登录请求
    await expect(page.locator('[data-testid="login-error"]')).not.toBeVisible();
  });

  test.skip("P0-AC5-02 - 应该验证密码不能为空", async ({ page }) => {
    // Given: 密码为空
    await page.fill('[data-testid="username-input"]', "test@example.com");

    // When: 尝试提交表单
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示密码验证错误
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toContainText(
      /密码不能为空|请输入密码/,
    );

    // Then: 不应该发送登录请求
    await expect(page.locator('[data-testid="login-error"]')).not.toBeVisible();
  });

  test.skip("P0-AC5-03 - 应该验证用户名和密码都为空", async ({ page }) => {
    // Given: 用户名和密码都为空

    // When: 尝试提交表单
    await page.click('[data-testid="login-button"]');

    // Then: 应该同时显示两个验证错误
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test.skip("P0-AC5-04 - 应该验证邮箱格式", async ({ page }) => {
    // Given: 无效的邮箱格式
    await page.fill('[data-testid="username-input"]', "invalid-email-format");
    await page.fill('[data-testid="password-input"]', "Test123456!");

    // When: 尝试提交表单
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示邮箱格式验证错误
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="username-error"]')).toContainText(
      /请输入有效的邮箱地址|邮箱格式不正确/,
    );
  });

  // ===========================================
  // 边界条件测试
  // ===========================================

  test.skip("P0-BC-01 - 应该支持超长用户名的处理", async ({ page }) => {
    // Given: 超长用户名（> 255 字符）
    const longEmail = "a".repeat(260) + "@example.com";
    await page.fill('[data-testid="username-input"]', longEmail);
    await page.fill('[data-testid="password-input"]', "Test123456!");

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 应该显示验证错误或拒绝登录（不应该崩溃）
    await expect(
      page.locator(
        '[data-testid="username-error"], [data-testid="login-error"]',
      ),
    ).toBeVisible();
  });

  test.skip("P0-BC-02 - 应该处理特殊字符密码", async ({ page, testData }) => {
    // Given: 包含特殊字符的密码
    const specialPassword = "Test@#$%^&*()_+-=[]{}|;:,.<>?123!";

    await page.fill('[data-testid="username-input"]', testData.user.email);
    await page.fill('[data-testid="password-input"]', specialPassword);

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 应该正常处理（拒绝或接受，但不应该崩溃）
    await expect(
      page.locator(
        '[data-testid="login-error"], [data-testid="welcome-message"]',
      ),
    ).toBeVisible();
  });

  test.skip("P0-BC-03 - 应该防止 SQL 注入攻击", async ({ page }) => {
    // Given: SQL 注入尝试的用户名
    const sqlInjectionEmail = "admin' OR '1'='1'@example.com";
    await page.fill('[data-testid="username-input"]', sqlInjectionEmail);
    await page.fill('[data-testid="password-input"]', "Test123456!");

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 应该拒绝登录（不应该成功）
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();

    // Then: 不应该显示数据库错误
    const errorMessage = await page
      .locator('[data-testid="login-error"]')
      .textContent();
    expect(errorMessage).not.toContain("SQL");
    expect(errorMessage).not.toContain("database");
    expect(errorMessage).not.toContain("syntax");
  });

  test.skip("P0-BC-04 - 应该防止 XSS 攻击", async ({ page }) => {
    // Given: XSS 攻击尝试的用户名
    const xssEmail = '<script>alert("XSS")</script>@example.com';
    await page.fill('[data-testid="username-input"]', xssEmail);
    await page.fill('[data-testid="password-input"]', "Test123456!");

    // When: 尝试登录
    await page.click('[data-testid="login-button"]');

    // Then: 应该拒绝登录
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();

    // Then: 不应该执行脚本
    const pageTitle = await page.title();
    expect(pageTitle).not.toContain("XSS");
  });

  // ===========================================
  // 用户体验测试
  // ===========================================

  test.skip("P0-UX-01 - 应该显示加载状态", async ({ page, testData }) => {
    // Given: 有效的登录凭据
    await page.fill('[data-testid="username-input"]', testData.user.email);
    await page.fill('[data-testid="password-input"]', testData.user.password);

    // When: 点击登录按钮
    await page.click('[data-testid="login-button"]');

    // Then: 登录按钮应该显示加载状态
    await expect(page.locator('[data-testid="login-button"]')).toBeDisabled();
    await expect(page.locator('[data-testid="login-loading"]')).toBeVisible();
  });

  test.skip("P0-UX-02 - 应该支持密码显示/隐藏切换", async ({ page }) => {
    // Given: 输入密码
    const password = "Test123456!";
    await page.fill('[data-testid="password-input"]', password);

    // When: 点击显示密码按钮
    await page.click('[data-testid="toggle-password-visibility"]');

    // Then: 密码应该显示为明文
    const passwordInput = page.locator('[data-testid="password-input"]');
    const inputType = await passwordInput.getAttribute("type");
    expect(inputType).toBe("text");

    // When: 再次点击隐藏密码
    await page.click('[data-testid="toggle-password-visibility"]');

    // Then: 密码应该再次隐藏
    const inputTypeAfter = await passwordInput.getAttribute("type");
    expect(inputTypeAfter).toBe("password");
  });

  test.skip("P0-UX-03 - 应该支持回车键登录", async ({ page, testData }) => {
    // Given: 输入登录凭据
    await page.fill('[data-testid="username-input"]', testData.user.email);
    await page.fill('[data-testid="password-input"]', testData.user.password);

    // When: 按回车键
    await page.press('[data-testid="password-input"]', "Enter");

    // Then: 应该触发登录并跳转到首页
    await expect(page).toHaveURL(/\/dashboard/);
  });
});
