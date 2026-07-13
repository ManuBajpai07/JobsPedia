import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    { 
      path: '/admin', 
      name: 'admin', 
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, role: 'ADMIN' }
    },
    {
      path: '/admin/search',
      name: 'adminSearch',
      component: () => import('../views/AdminSearchView.vue'),
      meta: { requiresAuth: true, role: 'ADMIN' }
    },
    { 
      path: '/company', 
      name: 'company', 
      component: () => import('../views/CompanyView.vue'),
      meta: { requiresAuth: true, role: 'COMPANY' }
    },
    { 
      path: '/student', 
      name: 'student', 
      component: () => import('../views/StudentView.vue'),
      meta: { requiresAuth: true, role: 'STUDENT' }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');

  if (to.meta.requiresAuth && !token) {
    next('/login');
  } else if (to.meta.requiresAuth && to.meta.role !== role) {
    next('/'); // Unauthorized, redirect home
  } else {
    next();
  }
});

export default router
