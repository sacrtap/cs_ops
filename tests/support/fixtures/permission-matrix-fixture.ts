/**
 * 权限矩阵夹具
 *
 * 提供权限测试数据，自动清理
 */

import { test as base } from "@playwright/test";
import {
  createDefaultPermissions,
  createRolePermissions,
  AllPermissions,
} from "../factories/permission-factory";

/**
 * 权限矩阵夹具类型
 */
type PermissionMatrixFixture = {
  permissionMatrix: AllPermissions;
  defaultPermissions: AllPermissions;
  customRolePermissions: (
    role: string,
    overrides?: Record<string, Record<string, boolean>>,
  ) => Promise<AllPermissions>;
};

/**
 * 扩展 Playwright test 夹具
 */
export const test = base.extend<PermissionMatrixFixture>({
  /**
   * 提供完整的权限矩阵数据
   */
  permissionMatrix: async ({}, use) => {
    // Setup: 创建默认权限矩阵
    const matrix = createDefaultPermissions();

    // Provide data to test
    await use(matrix);

    // Teardown: 清理（权限矩阵不需要清理，因为是只读数据）
  },

  /**
   * 提供默认权限配置
   */
  defaultPermissions: async ({}, use) => {
    // Setup: 创建默认权限
    const defaults = createDefaultPermissions();

    // Provide data to test
    await use(defaults);

    // Teardown: 不需要清理
  },

  /**
   * 创建自定义角色权限
   */
  customRolePermissions: async ({}, use) => {
    // Setup function
    const createCustom = async (
      role: string,
      overrides?: Record<string, Record<string, boolean>>,
    ): Promise<AllPermissions> => {
      const permissions = createRolePermissions(role, overrides);
      return { [role]: permissions };
    };

    // Provide function to test
    await use(createCustom);

    // Teardown: 如果有创建测试数据，在这里清理
  },
});

export { expect } from "@playwright/test";
