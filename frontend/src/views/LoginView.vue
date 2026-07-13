<template>
  <div class="container py-5 mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card p-4 shadow-sm border-0">
          <h2 class="text-center mb-4">Login</h2>
          <form @submit.prevent="handleLogin">
            <div class="mb-3">
              <label class="form-label fw-bold">Email</label>
              <input type="email" class="form-control" v-model="email" required>
            </div>
            <div class="mb-4">
              <label class="form-label fw-bold">Password</label>
              <input type="password" class="form-control" v-model="password" required>
            </div>
            
            <div v-if="error" class="alert alert-danger p-2 mb-3">{{ error }}</div>

            <button type="submit" class="btn btn-primary w-100" :disabled="loading">
              {{ loading ? 'Logging in...' : 'Login' }}
            </button>
            <div class="text-center mt-4">
              <span>Don't have an account?</span>
              <router-link to="/register" class="fw-bold ms-2 text-decoration-none">Sign Up</router-link>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../services/api';

export default {
  data() {
    return {
      email: '',
      password: '',
      loading: false,
      error: ''
    }
  },
  methods: {
    async handleLogin() {
      this.loading = true;
      this.error = '';
      try {
        const response = await api.post('/auth/login', {
          email: this.email,
          password: this.password
        });
        
        localStorage.setItem('token', response.data.access_token);
        localStorage.setItem('role', response.data.role);
        localStorage.setItem('name', response.data.name);
        
        if (response.data.role === 'ADMIN') {
          this.$router.push('/admin');
        } else if (response.data.role === 'COMPANY') {
          this.$router.push('/company');
        } else {
          this.$router.push('/student');
        }
      } catch (err) {
        this.error = err.response?.data?.message || 'Login failed. Please check credentials.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
