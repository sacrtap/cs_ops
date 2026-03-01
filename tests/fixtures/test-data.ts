// Fixtures for ATDD tests
export const testRoleData = {
  id: 1,
  name: 'Admin',
  description: 'System administrator with full permissions',
};

export const testUserData = {
  id: 1,
  email: 'admin@example.com',
  password: 'admin123',
  role: 'Admin',
};

export const testRolePermissions = [
  {
    role_id: 1,
    module: 'user',
    operation: 'read',
  },
  {
    role_id: 1,
    module: 'user',
    operation: 'create',
  },
  {
    role_id: 1,
    module: 'user',
    operation: 'update',
  },
  {
    role_id: 1,
    module: 'user',
    operation: 'delete',
  },
  {
    role_id: 1,
    module: 'role',
    operation: 'read',
  },
  {
    role_id: 1,
    module: 'role',
    operation: 'create',
  },
  {
    role_id: 1,
    module: 'role',
    operation: 'update',
  },
  {
    role_id: 1,
    module: 'role',
    operation: 'delete',
  },
  {
    role_id: 1,
    module: 'data_permission',
    operation: 'read',
  },
  {
    role_id: 1,
    module: 'data_permission',
    operation: 'create',
  },
  {
    role_id: 1,
    module: 'data_permission',
    operation: 'update',
  },
  {
    role_id: 1,
    module: 'data_permission',
    operation: 'delete',
  },
  {
    role_id: 1,
    module: 'function_permission',
    operation: 'read',
  },
  {
    role_id: 1,
    module: 'function_permission',
    operation: 'create',
  },
  {
    role_id: 1,
    module: 'function_permission',
    operation: 'update',
  },
  {
    role_id: 1,
    module: 'function_permission',
    operation: 'delete',
  },
];
