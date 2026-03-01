import { test, expect } from "@playwright/test";

test.describe("[Story 1.6] Role Management API Tests (ATDD)", () => {
  test("[P0] should get role list successfully", async ({ request }) => {
    // THIS TEST WILL FAIL - Endpoint not implemented yet
    const response = await request.get("/api/v1/roles");
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ name: "Admin" }),
        expect.objectContaining({ name: "经理" }),
        expect.objectContaining({ name: "专员" }),
        expect.objectContaining({ name: "销售" }),
      ]),
    );
  });

  test("[P0] should get role permissions successfully", async ({ request }) => {
    // THIS TEST WILL FAIL - Endpoint not implemented yet
    const roleId = 1;
    const response = await request.get(`/api/v1/roles/${roleId}/permissions`);
    expect(response.status()).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty("role_id", roleId);
    expect(data).toHaveProperty("permissions");
    expect(data.permissions).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ module: "user" }),
        expect.objectContaining({ module: "role" }),
        expect.objectContaining({ module: "data_permission" }),
        expect.objectContaining({ module: "function_permission" }),
      ]),
    );
  });

  test("[P0] should update role permissions successfully", async ({
    request,
  }) => {
    // THIS TEST WILL FAIL - Endpoint not implemented yet
    const roleId = 2;
    const response = await request.put(`/api/v1/roles/${roleId}/permissions`, {
      data: {
        permissions: [
          {
            module: "user",
            operations: ["read", "create", "update"],
          },
          {
            module: "role",
            operations: ["read"],
          },
          {
            module: "data_permission",
            operations: ["read"],
          },
          {
            module: "function_permission",
            operations: ["read"],
          },
        ],
      },
    });
    expect(response.status()).toBe(200);
  });

  test("[P1] should create role successfully", async ({ request }) => {
    // THIS TEST WILL FAIL - Endpoint not implemented yet
    const response = await request.post("/api/v1/roles", {
      data: {
        name: "Test Role",
        description: "Test role description",
        permissions: [],
      },
    });
    expect(response.status()).toBe(201);
    const data = await response.json();
    expect(data).toHaveProperty("id");
    expect(data).toHaveProperty("name", "Test Role");
  });

  test("[P1] should update role successfully", async ({ request }) => {
    // THIS TEST WILL FAIL - Endpoint not implemented yet
    const roleId = 5;
    const response = await request.put(`/api/v1/roles/${roleId}`, {
      data: {
        description: "Updated role description",
      },
    });
    expect(response.status()).toBe(200);
  });

  test("[P1] should delete role successfully", async ({ request }) => {
    // THIS TEST WILL FAIL - Endpoint not implemented yet
    const roleId = 5;
    const response = await request.delete(`/api/v1/roles/${roleId}`);
    expect(response.status()).toBe(200);
  });
});
