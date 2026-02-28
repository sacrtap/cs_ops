/**
 * 示例 E2E 测试 - 客户管理模块
 *
 * 演示测试模式：
 * 1. Given-When-Then 结构
 * 2. data-testid 选择器策略
 * 3. 数据工厂使用
 * 4. 网络拦截模式
 */

import { test, expect } from "../../support/fixtures";
import { DataFactory } from "../../support/fixtures/index";

test.describe("客户管理模块 E2E 测试", () => {
  test.beforeEach(async ({ page }) => {
    // 导航到客户列表页
    await page.goto("/customers");
  });

  test("应该成功创建新客户", async ({ page, testData }) => {
    // Given: 访问客户列表页面
    await expect(page).toHaveURL(/\/customers/);

    // When: 点击"新建客户"按钮
    await page.click('[data-testid="new-customer-button"]');

    // Then: 应该显示新建客户表单
    await expect(page.locator('[data-testid="customer-form"]')).toBeVisible();

    // When: 填写客户信息
    const customerData = DataFactory.createCustomer();

    await page.fill('[data-testid="customer-name-input"]', customerData.name);
    await page.fill('[data-testid="customer-email-input"]', customerData.email);
    await page.fill('[data-testid="customer-phone-input"]', customerData.phone);

    // When: 提交表单
    await page.click('[data-testid="submit-button"]');

    // Then: 应该显示成功提示
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();

    // Then: 应该 redirect 到客户列表页
    await expect(page).toHaveURL(/\/customers/);

    // Then: 列表中应该显示新客户
    await expect(
      page.locator(`[data-testid="customer-row-${customerData.name}"]`),
    ).toBeVisible();
  });

  test("应该成功编辑现有客户", async ({ page }) => {
    // Given: 列表中已有一个客户
    const customerName = "测试客户公司";

    // When: 点击编辑按钮
    await page.click(`[data-testid="edit-customer-button-${customerName}"]`);

    // Then: 应该显示编辑表单
    await expect(page.locator('[data-testid="customer-form"]')).toBeVisible();

    // When: 修改客户信息
    const newEmail = "updated@example.com";
    await page.fill('[data-testid="customer-email-input"]', newEmail);

    // When: 保存修改
    await page.click('[data-testid="submit-button"]');

    // Then: 应该显示成功提示
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();

    // Then: 列表中应该显示更新后的邮箱
    await expect(
      page.locator(`[data-testid="customer-email-${newEmail}"]`),
    ).toBeVisible();
  });

  test("应该成功删除客户", async ({ page }) => {
    // Given: 列表中已有一个客户
    const customerName = "待删除客户公司";

    // When: 点击删除按钮
    await page.click(`[data-testid="delete-customer-button-${customerName}"]`);

    // Then: 应该显示确认对话框
    await expect(page.locator('[data-testid="confirm-dialog"]')).toBeVisible();

    // When: 确认删除
    await page.click('[data-testid="confirm-delete-button"]');

    // Then: 应该显示成功提示
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();

    // Then: 客户应该从列表中消失
    await expect(
      page.locator(`[data-testid="customer-row-${customerName}"]`),
    ).not.toBeVisible();
  });

  test("应该支持批量导入客户", async ({ page }) => {
    // Given: 访问客户列表页
    await expect(page).toHaveURL(/\/customers/);

    // When: 点击"批量导入"按钮
    await page.click('[data-testid="bulk-import-button"]');

    // Then: 应该显示导入对话框
    await expect(page.locator('[data-testid="import-dialog"]')).toBeVisible();

    // When: 上传 Excel 文件
    const fileChooserPromise = page.waitForEvent("filechooser");
    await page.click('[data-testid="file-upload-area"]');
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles(
      "./tests/support/fixtures/test-data/customers.xlsx",
    );

    // Then: 应该显示导入预览
    await expect(page.locator('[data-testid="import-preview"]')).toBeVisible();

    // When: 确认导入
    await page.click('[data-testid="confirm-import-button"]');

    // Then: 应该显示成功提示
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();

    // Then: 应该显示导入结果摘要
    await expect(page.locator('[data-testid="import-summary"]')).toContainText(
      /成功导入 \d+ 条记录/,
    );
  });

  test("应该支持客户数据验证", async ({ page }) => {
    // Given: 打开新建客户表单
    await page.click('[data-testid="new-customer-button"]');

    // When: 输入无效的邮箱格式
    await page.fill('[data-testid="customer-email-input"]', "invalid-email");

    // When: 尝试提交
    await page.click('[data-testid="submit-button"]');

    // Then: 应该显示验证错误
    await expect(page.locator('[data-testid="email-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="email-error"]')).toContainText(
      "请输入有效的邮箱地址",
    );

    // Then: 表单不应该提交
    await expect(
      page.locator('[data-testid="success-message"]'),
    ).not.toBeVisible();
  });
});
