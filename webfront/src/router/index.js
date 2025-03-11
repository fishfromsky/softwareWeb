import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../views/Login/index.vue'
import Register from '../views/Register/index.vue'
import dynamicPage from '@/views/Components/dynamicPage.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/Register',
    name: 'Register',
    component: Register
  },
]

const router = new VueRouter({
  mode: 'history',
  routes
})

export default router
