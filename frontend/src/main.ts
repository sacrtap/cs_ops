import { createApp } from "vue";
import { createPinia } from "pinia";
import ArcoVue from "@arco-design/web-vue";
import "@arco-design/web-vue/dist/arco.css";
import App from "./App.vue";
import router from "./router";

// 创建 Vue 应用实例
const app = createApp(App);

// 创建 Pinia 状态管理实例
const pinia = createPinia();

// 注册插件
app.use(pinia);
app.use(router);
app.use(ArcoVue);

// 挂载到 DOM
app.mount("#app");
