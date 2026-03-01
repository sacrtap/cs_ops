/**
 * 权限认证夹具
 *
 * 提供认证用户和 JWT token，自动清理
 */

import { test as base, APIRequestContext } from "@playwright/test";
import {
  createAdminUser,
  createSalesUser,
  createManagerUser,
  UserData,
} from "../factories/user-factory";

/**
 * 认证用户数据类型
 */
interface AuthenticatedUser {
  user: UserData;
  token: string;
  refreshToken?: string;
}

/**
 * 权限认证夹具类型
 */
type PermissionAuthFixture = {
  authenticatedUser: (role: string) => Promise<AuthenticatedUser>;
  adminUser: Promise<AuthenticatedUser>;
  salesUser: Promise<AuthenticatedUser>;
  managerUser: Promise<AuthenticatedUser>;
};

/**
 * 用户登录并获取 token
 */
async function loginUser(
  request: APIRequestContext,
  user: UserData,
): Promise<AuthenticatedUser> {
  const loginResponse = await request.post("/api/v1/auth/login", {
    data: {
      username: user.username,
      password: user.password,
    },
  });

  if (!loginResponse.ok()) {
    throw new Error(
      `Login failed: ${loginResponse.status()} ${await loginResponse.text()}`,
    );
  }

  const authData = await loginResponse.json();

  return {
    user,
    token: authData.data.token,
    refreshToken: authData.data.refreshToken,
  };
}

/**
 * 扩展 Playwright test 夹具
 */
export const test = base.extend<PermissionAuthFixture>({
  /**
   * 提供指定角色的认证用户
   */
  authenticatedUser: async ({ request }, use) => {
    // Setup function
    const authenticate = async (role: string): Promise<AuthenticatedUser> => {
      let user: UserData;

      switch (role) {
        case "admin":
          user = createAdminUser();
          break;
        case "sales":
          user = createSalesUser();
          break;
        case "manager":
          user = createManagerUser();
          break;
        default:
          user = createSalesUser();
      }

      return await loginUser(request, user);
    };

    // Provide function to test
    await use(authenticate);

    // Teardown: 如果需要，可以在这里使 token 失效
  },

  /**
   * 提供 Admin 认证用户
   */
  adminUser: async ({ request }, use) => {
    // Setup: 创建并登录 Admin 用户
    const user = createAdminUser();
    const auth = await loginUser(request, user);

    // Provide to test
    await use(auth);

    // Teardown: 可选 - 使 token 失效
    // await request.post('/api/v1/auth/logout', {
    //   headers: { Authorization: `Bearer ${auth.token}` },
    // });
  },

  /**
   * 提供销售认证用户
   */
  salesUser: async ({ request }, use) => {
    // Setup: 创建并登录销售用户
    const user = createSalesUser();
    const auth = await loginUser(request, user);

    // Provide to test
    await use(auth);

    // Teardown: 可选
  },

  /**
   * 提供经理认证用户
   */
  managerUser: async ({ request }, use) => {
    // Setup: 创建并登录经理用户
    const user = createManagerUser();
    const auth = await loginUser(request, user);

    // Provide to test
    await use(auth);

    // Teardown: 可选
  },
});

export { expect } from "@playwright/test";
