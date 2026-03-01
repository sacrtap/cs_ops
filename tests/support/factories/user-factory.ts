/**
 * 用户数据工厂（增强现有 user-factory）
 *
 * 使用 Faker 生成测试用户数据，支持指定角色
 */

import { faker } from "@faker-js/faker";

export interface UserData {
  username: string;
  email: string;
  password: string;
  role: string;
  org_id?: number;
  sales_rep_id?: number;
}

/**
 * 创建指定角色的用户
 */
export function createUserWithRole(
  role: string,
  overrides?: Partial<UserData>,
): UserData {
  return {
    username: faker.internet.userName(),
    email: faker.internet.email(),
    password: process.env.TEST_USER_PASSWORD || "Test123456!",
    role: role,
    org_id: faker.number.int({ min: 1, max: 100 }),
    ...overrides,
  };
}

/**
 * 创建 Admin 用户
 */
export function createAdminUser(overrides?: Partial<UserData>): UserData {
  return createUserWithRole("admin", {
    username: overrides?.username || "admin_test",
    email: overrides?.email || "admin@test.com",
    ...overrides,
  });
}

/**
 * 创建经理用户
 */
export function createManagerUser(overrides?: Partial<UserData>): UserData {
  return createUserWithRole("manager", {
    username: overrides?.username || "manager_test",
    email: overrides?.email || "manager@test.com",
    ...overrides,
  });
}

/**
 * 创建专员用户
 */
export function createSpecialistUser(overrides?: Partial<UserData>): UserData {
  return createUserWithRole("specialist", {
    username: overrides?.username || "specialist_test",
    email: overrides?.email || "specialist@test.com",
    ...overrides,
  });
}

/**
 * 创建销售用户
 */
export function createSalesUser(overrides?: Partial<UserData>): UserData {
  return createUserWithRole("sales", {
    username: overrides?.username || "sales_test",
    email: overrides?.email || "sales@test.com",
    sales_rep_id:
      overrides?.sales_rep_id || faker.number.int({ min: 1, max: 1000 }),
    ...overrides,
  });
}

/**
 * 批量创建用户
 */
export function createUsersBatch(count: number, role?: string): UserData[] {
  const roles = ["admin", "manager", "specialist", "sales"];

  return Array.from({ length: count }, () => {
    const selectedRole = role || faker.helpers.arrayElement(roles);
    return createUserWithRole(selectedRole);
  });
}
