import Vue from 'vue'
import VueRouter from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Generate from '../views/components/Generate/index.vue'
import Manage from '../views/components/Manage/index.vue'
import Person from '../views/components/Person/index.vue'
import Login from '../views/components/Login/index.vue'
import Register from '../views/components/Register/index.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    redirect: '/generate',
    children: [
      {
        path: '/generate',
        name: 'generate',
        component: Generate,
        meta: { requiresAuth: true }
      },
      {
        path: '/manage',
        name: 'manage',
        component: Manage,
        meta: { requiresAuth: true }
      },
      {
        path: '/person',
        name: 'person',
        component: Person,
        meta: { requiresAuth: true }
      }
    ]
  },
  {
    path: '/register',
    name: 'register',
    component: Register
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  }
]

const router = new VueRouter({
  mode: 'history',
  routes
})

router.beforeEach((to, from, next) => {
  const isAuthenticated = document.cookie.split(';').some(c => c.trim().startsWith('username='))
  if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
    next('/login')
  } else if (!isAuthenticated && to.path !== '/login' && to.path !== '/register') {
    next('/login')
  } else {
    next()
  }
})

export default router
