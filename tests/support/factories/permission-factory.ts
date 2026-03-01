/**
 * 权限矩阵数据工厂
 *
 * 使用 Faker 生成测试数据，支持覆盖特定字段
 */

import { faker } from "@faker-js/faker";

export interface PermissionMatrixData {
  role: string;
  module: string;
  action: string;
  granted: boolean;
}

export interface RolePermissions {
  [module: string]: {
    [action: string]: boolean;
  };
}

export interface AllPermissions {
  [role: string]: RolePermissions;
}

/**
 * 创建单个权限矩阵数据
 */
export function createPermissionMatrix(
  overrides?: Partial<PermissionMatrixData>,
): PermissionMatrixData {
  const roles = ["admin", "manager", "specialist", "sales"];
  const modules = ["customer", "settlement", "reporting", "permission"];
  const actions = ["read", "create", "update", "delete"];

  return {
    role: faker.helpers.arrayElement(roles),
    module: faker.helpers.arrayElement(modules),
    action: faker.helpers.arrayElement(actions),
    granted: faker.datatype.boolean(),
    ...overrides,
  };
}

/**
 * 创建角色的所有权限
 */
export function createRolePermissions(
  role: string,
  overrides?: Record<string, Record<string, boolean>>,
): RolePermissions {
  const modules = ["customer", "settlement", "reporting", "permission"];
  const actions = ["read", "create", "update", "delete"];

  const permissions: RolePermissions = {};

  modules.forEach((module) => {
    permissions[module] = {};
    actions.forEach((action) => {
      // 使用覆盖值或生成随机值
      if (overrides?.[module]?.[action] !== undefined) {
        permissions[module][action] = overrides[module][action];
      } else {
        // Admin 默认全 true，其他角色默认随机
        permissions[module][action] =
          role === "admin" ? true : faker.datatype.boolean();
      }
    });
  });

  return permissions;
}

/**
 * 创建默认权限配置（符合业务规则）
 */
export function createDefaultPermissions(): AllPermissions {
  return {
    admin: {
      customer: { read: true, create: true, update: true, delete: true },
      settlement: { read: true, create: true, update: true, delete: true },
      reporting: { read: true, create: true, update: true, delete: true },
      permission: { read: true, create: true, update: true, delete: true },
    },
    manager: {
      customer: { read: true, create: true, update: true, delete: false },
      settlement: { read: true, create: false, update: true, delete: false },
      reporting: { read: true, create: false, update: false, delete: false },
      permission: { read: true, create: false, update: false, delete: false },
    },
    specialist: {
      customer: { read: true, create: true, update: true, delete: false },
      settlement: { read: true, create: true, update: true, delete: false },
      reporting: { read: true, create: false, update: false, delete: false },
      permission: { read: true, create: false, update: false, delete: false },
    },
    sales: {
      customer: { read: true, create: false, update: true, delete: false },
      settlement: { read: true, create: false, update: false, delete: false },
      reporting: { read: false, create: false, update: false, delete: false },
      permission: { read: false, create: false, update: false, delete: false },
    },
  };
}

/**
 * 批量创建权限矩阵数据
 */
export function createPermissionMatrixBatch(
  count: number,
  overrides?: Partial<PermissionMatrixData>,
): PermissionMatrixData[] {
  return Array.from({ length: count }, () => createPermissionMatrix(overrides));
}

/**
 * 创建特定角色的最小权限配置（用于测试权限不足场景）
 */
export function createMinimalPermissions(role: string): RolePermissions {
  return {
    customer: { read: true, create: false, update: false, delete: false },
    settlement: { read: false, create: false, update: false, delete: false },
    reporting: { read: false, create: false, update: false, delete: false },
    permission: { read: false, create: false, update: false, delete: false },
  };
}

/**
 * 创建特定角色的最大权限配置（用于测试权限充足场景）
 */
export function createMaximalPermissions(role: string): RolePermissions {
  if (role === "admin") {
    return {
      customer: { read: true, create: true, update: true, delete: true },
      settlement: { read: true, create: true, update: true, delete: true },
      reporting: { read: true, create: true, update: true, delete: true },
      permission: { read: true, create: true, update: true, delete: true },
    };
  }

  // 非 Admin 角色给予接近 Admin 的权限（用于测试边界情况）
  return {
    customer: { read: true, create: true, update: true, delete: true },
    settlement: { read: true, create: true, update: true, delete: true },
    reporting: { read: true, create: true, update: true, delete: false },
    permission: { read: true, create: false, update: false, delete: false },
  };
}
