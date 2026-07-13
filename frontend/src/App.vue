<template>
  <div id="app-wrapper" class="d-flex flex-column min-vh-100">
    <nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom">
      <div class="container">
        <router-link class="navbar-brand fw-bold" to="/">JobsPedia.</router-link>
        
        <!-- Center/Left: Admin Search Bar -->
        <div v-if="userRole === 'ADMIN' && $route.path.startsWith('/admin')" class="mx-auto" style="max-width: 400px; width: 100%;">
           <div class="input-group">
             <input type="text" class="form-control" placeholder="Search students, organizations" v-model="adminSearchQuery" @keyup.enter="emitSearch">
             <button class="btn btn-primary" @click="emitSearch">Search</button>
           </div>
        </div>
        
        <ul class="navbar-nav ms-auto flex-row gap-3">
          <template v-if="!isLoggedIn">
            <li class="nav-item">
              <router-link class="nav-link" to="/login">Login</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/register">Sign Up</router-link>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
               <span class="nav-link">Welcome {{ userName }}</span>
            </li>
            <li class="nav-item" v-if="$route.path === '/'">
              <router-link class="nav-link" :to="dashboardRoute">Dashboard</router-link>
            </li>
          </template>
        </ul>
      </div>
    </nav>

    <main class="flex-grow-1">
      <router-view />
    </main>

    <footer class="text-center py-4 border-top mt-auto bg-light">
      <div class="container">
        <div class="d-flex justify-content-center gap-3">
          <a href="https://github.com/Manubajpai/JobsPedia" target="_blank" rel="noopener noreferrer" class="text-decoration-none">GitHub</a>
          <a href="https://www.instagram.com/_manubajpai/" target="_blank" rel="noopener noreferrer" class="text-decoration-none">Instagram</a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      isLoggedIn: false,
      userRole: null,
      userName: '',
      adminSearchQuery: ''
    }
  },
  computed: {
    dashboardRoute() {
      if (this.userRole === 'ADMIN') return '/admin';
      if (this.userRole === 'COMPANY') return '/company';
      return '/student';
    }
  },
  watch: {
    $route() {
      this.checkAuth();
    }
  },
  mounted() {
    this.checkAuth();
  },
  methods: {
    checkAuth() {
      this.isLoggedIn = !!localStorage.getItem('token');
      this.userRole = localStorage.getItem('role');
      this.userName = localStorage.getItem('name') || '';
    },
    emitSearch() {
      if (this.adminSearchQuery.trim()) {
        this.$router.push({ path: '/admin/search', query: { q: this.adminSearchQuery } });
      }
    }
  }
}
</script>
