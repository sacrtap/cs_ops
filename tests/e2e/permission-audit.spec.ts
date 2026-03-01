import { test, expect } from "@playwright/test";

/**
 * ATDD E2E Tests for Permission Audit (Story 1.8)
 *
 * Story: 权限审计
 * As a Admin,
 * I want 查看权限使用日志，
 * so that 审计权限合规性.
 *
 * TDD Phase: GREEN (测试已启用，等待运行)
 *
 * 运行方式:
 * 1. 确保后端服务和前端服务都运行
 * 2. 运行测试：npx playwright test tests/e2e/permission-audit.spec.ts
 */

test.describe("[Story 1.8] 权限审计 E2E 测试 (ATDD)", () => {
  /**
   * 验收标准 1: Admin 进入权限审计页面
   * Given Admin 进入权限审计页面
   * When 页面加载
   * Then 验证权限
   * And 显示审计页面
   */

  test("[P0] 应该导航到权限审计页面", async ({ page }) => {
    // 期望：用户可以导航到权限审计页面
    await page.goto("/");
    // 登录（需要 admin 权限）
    await page.fill('[name="username"]', "admin");
    await page.fill('[name="password"]', "admin123");
    await page.click('button:has-text("登录")');
    // 导航到权限审计页面
    await page.click('a:has-text("权限管理")');
    await page.click('a:has-text("权限审计")');
    // 验证页面标题
    await expect(page.getByText("权限审计")).toBeVisible();
  });

  /**
   * 验收标准 2: 选择用户/日期范围
   * Given 进入权限审计页面
   * When 选择用户/日期范围
   * Then 查询权限使用记录
   */

  test("[P0] 应该支持用户选择功能", async ({ page }) => {
    // 期望：用户可以选择要审计的用户
    await page.goto("/permissions/audit");
    // 选择用户
    await page.selectOption('select[name="user"]', "123");
    // 验证选择是否成功
    await expect(page.getByText("用户 ID: 123")).toBeVisible();
  });

  test("[P0] 应该支持日期范围选择功能", async ({ page }) => {
    // 期望：用户可以选择日期范围
    await page.goto("/permissions/audit");
    // 选择日期范围
    await page.fill('[name="start_date"]', "2026-01-01");
    await page.fill('[name="end_date"]', "2026-01-31");
    // 点击查询按钮
    await page.click('button:has-text("查询")');
    // 验证查询是否成功
    await expect(page.getByText("查询成功")).toBeVisible();
  });

  /**
   * 验收标准 3: 显示权限使用记录
   * Given 选择了查询条件
   * When 提交查询
   * Then 显示权限使用记录列表
   */

  test("[P0] 应该显示权限使用记录列表", async ({ page }) => {
    // 期望：显示权限使用记录列表
    await page.goto("/permissions/audit");
    // 执行查询
    await page.click('button:has-text("查询")');
    // 验证记录列表是否显示
    await expect(page.getByRole("table")).toBeVisible();
    const rows = await page.getByRole("row").count();
    await expect(rows).toBeGreaterThan(1);
  });

  test("[P1] 应该支持分页功能", async ({ page }) => {
    // 期望：支持分页功能
    await page.goto("/permissions/audit");
    // 执行查询
    await page.click('button:has-text("查询")');
    // 验证分页控件是否显示
    await expect(page.getByText("上一页")).toBeVisible();
    await expect(page.getByText("下一页")).toBeVisible();
    await expect(page.getByText("共 X 页")).toBeVisible();
  });

  test("[P1] 应该支持排序功能", async ({ page }) => {
    // 期望：支持排序功能
    await page.goto("/permissions/audit");
    // 执行查询
    await page.click('button:has-text("查询")');
    // 点击时间戳列标题进行排序
    await page.click('th:has-text("时间")');
    // 验证排序是否生效
    await expect(page.getByText("正在排序")).toBeVisible();
  });

  /**
   * 验收标准 4: 标记异常访问
   * Given 权限审计记录已显示
   * When 系统检测到异常访问
   * Then 标记异常访问记录
   */

  test("[P1] 应该标记异常访问记录", async ({ page }) => {
    // 期望：异常访问记录会被标记
    await page.goto("/permissions/audit");
    // 执行查询
    await page.click('button:has-text("查询")');
    // 验证异常访问记录是否被标记
    await expect(page.getByText("异常访问")).toBeVisible();
    await expect(page.getByRole("cell", { name: "异常访问" })).toHaveCSS(
      "background-color",
      "rgba(255, 0, 0, 0.1)",
    );
  });

  test("[P1] 应该显示异常访问统计信息", async ({ page }) => {
    // 期望：显示异常访问统计信息
    await page.goto("/permissions/audit");
    // 执行查询
    await page.click('button:has-text("查询")');
    // 验证统计信息是否显示
    await expect(page.getByText("异常访问数量")).toBeVisible();
    await expect(page.getByText("异常访问率")).toBeVisible();
  });

  test("[P2] 应该支持异常访问类型筛选", async ({ page }) => {
    // 期望：支持按异常访问类型筛选
    await page.goto("/permissions/audit");
    // 选择异常访问类型
    await page.selectOption(
      'select[name="anomaly_type"]',
      "unauthorized_access",
    );
    // 执行查询
    await page.click('button:has-text("查询")');
    // 验证结果是否只包含未授权访问
    const anomalyCells = await page
      .getByRole("cell", {
        name: "未授权访问",
      })
      .count();
    await expect(anomalyCells).toBeGreaterThan(0);
  });

  test("[P3] 应该支持导出权限审计记录", async ({ page }) => {
    // 期望：支持导出权限审计记录
    await page.goto("/permissions/audit");
    // 执行查询
    await page.click('button:has-text("查询")');
    // 点击导出按钮
    await page.click('button:has-text("导出")');
    // 验证导出功能是否正常
    await expect(page.getByText("导出成功")).toBeVisible();
  });
});
