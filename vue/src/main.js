import Vue from 'vue'
import App from './App.vue'
import router from './router'
import AsyncComputed from 'vue-async-computed'
Vue.use(AsyncComputed)
import axios from 'axios'

// Bootstrap
import BootstrapVue from 'bootstrap-vue'

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(BootstrapVue)

// Axios setup
axios.defaults.xsrfHeaderName = "X-CSRFToken";
axios.defaults.xsrfCookieName = "xsrfcookie";
axios.defaults.withCredentials = true;

Vue.prototype.$APIConstants = {
  REST_PAGE_SIZE: 100,
  API_LOGIN: "/api/auth/login/?next=/",
  API_LOGOUT: "/api/auth/logout/?next=/",
}

export const HTTP = axios.create({
  baseURL: process.env.VUE_APP_API_ENDPOINT
})

Vue.config.productionTip = false

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
