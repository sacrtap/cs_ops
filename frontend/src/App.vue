<template>
  <router-view />
</template>

<script setup lang="ts">
/**
 * 根组件
 *
 * 负责：
 * 1. 提供路由出口
 * 2. 全局样式和布局
 * 3. 应用级配置
 */
</script>

<style lang="less">
// 全局样式重置
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

// HTML 和 Body 基础样式
html,
body {
  width: 100%;
  height: 100%;
  font-family:
    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue",
    Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji",
    "Segoe UI Symbol", "Noto Color Emoji";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

// 应用根容器
#app {
  width: 100%;
  height: 100%;
}

// 滚动条美化（Webkit 浏览器）
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;

  &:hover {
    background: #a8a8a8;
  }
}

// Arco Design 主题定制（可选）
// :root {
//   --primary-color: #165dff;
//   --success-color: #00b42a;
//   --warning-color: #ff7d00;
//   --danger-color: #f53f3f;
// }
</style>
