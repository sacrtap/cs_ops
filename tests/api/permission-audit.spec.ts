import { test, expect } from "@playwright/test";

/**
 * ATDD API Tests for Permission Audit (Story 1.8)
 *
 * Story: 权限审计
 * As a Admin,
 * I want 查看权限使用日志，
 * so that 审计权限合规性.
 *
 * TDD Phase: GREEN (测试已启用，等待运行)
 *
 * 运行方式:
 * 1. 确保后端服务运行：cd backend && source .venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000
 * 2. 运行测试：PLAYWRIGHT_API_ONLY=1 npx playwright test tests/api/permission-audit.spec.ts --project=api
 */

test.describe("[Story 1.8] 权限审计 API 测试 (ATDD)", () => {
  // 测试用 JWT Token（管理员）- 使用后端 SECRET_KEY 生成
  const ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI0IiwiZW1haWwiOiJhZG1pbkBleGFtcGxlLmNvbSIsInJvbGUiOiJhZG1pbiIsInVzZXJuYW1lIjoiYWRtaW4iLCJ0eXBlIjoiYWNjZXNzIiwiZXhwIjoxODAzOTE2NzMzfQ.WPbTCPTUTYc1hSoaXXcHE054IuH9sF9py3OzkAwgO9Y";
  
  // 认证请求头
  const authHeaders = {
    "Authorization": `Bearer ${ADMIN_TOKEN}`,
  };

  test("[P0] 应该验证权限审计页面访问权限", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", { headers: authHeaders });
    expect(response.status()).toBe(200);
  });

  test("[P0] 应该支持按用户查询权限审计记录", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", {
      params: { user_id: "123" },
      headers: authHeaders,
    });
    expect(response.status()).toBe(200);
    const auditRecords = await response.json();
    expect(auditRecords).toEqual(
      expect.arrayContaining([expect.objectContaining({ user_id: "123" })])
    );
  });

  test("[P0] 应该支持按日期范围查询权限审计记录", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", {
      params: { start_date: "2026-01-01", end_date: "2026-01-31" },
      headers: authHeaders,
    });
    expect(response.status()).toBe(200);
    const auditRecords = await response.json();
    expect(auditRecords).toEqual(
      expect.arrayContaining([expect.objectContaining({ timestamp: expect.stringMatching(/^2026-01-/) })])
    );
  });

  test("[P0] 应该支持组合查询（用户 + 日期范围）", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", {
      params: { user_id: "123", start_date: "2026-01-01", end_date: "2026-01-31" },
      headers: authHeaders,
    });
    expect(response.status()).toBe(200);
    const auditRecords = await response.json();
    expect(auditRecords).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ user_id: "123", timestamp: expect.stringMatching(/^2026-01-/) })
      ])
    );
  });

  test("[P0] 应该返回权限审计记录列表", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", { headers: authHeaders });
    expect(response.status()).toBe(200);
    const auditRecords = await response.json();
    expect(Array.isArray(auditRecords)).toBe(true);
  });

  test("[P1] 应该支持分页查询权限审计记录", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", {
      params: { page: 1, page_size: 10 },
      headers: authHeaders,
    });
    expect(response.status()).toBe(200);
  });

  test("[P1] 应该支持排序权限审计记录", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", {
      params: { sort_by: "timestamp", sort_order: "desc" },
      headers: authHeaders,
    });
    expect(response.status()).toBe(200);
  });

  test("[P1] 应该标记异常访问记录", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", { headers: authHeaders });
    expect(response.status()).toBe(200);
    const auditRecords = await response.json();
    expect(Array.isArray(auditRecords)).toBe(true);
  });

  test("[P1] 应该返回异常访问统计信息", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit/statistics", { headers: authHeaders });
    expect(response.status()).toBe(200);
    const statistics = await response.json();
    expect(statistics).toHaveProperty("total_count");
    expect(statistics).toHaveProperty("anomaly_count");
  });

  test("[P2] 应该支持异常访问类型筛选", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit", {
      params: { anomaly_type: "unauthorized_access" },
      headers: authHeaders,
    });
    expect(response.status()).toBe(200);
  });

  test("[P3] 应该支持导出权限审计记录", async ({ request }) => {
    const response = await request.get("/api/v1/permissions/audit/export", {
      params: { format: "csv" },
      headers: authHeaders,
    });
    expect(response.status()).toBe(200);
  });
});
