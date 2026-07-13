<template>
  <div class="container py-5 mt-4">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card p-4 shadow-sm border-0">
          <h2 class="text-center mb-4">Create Account</h2>
          
          <ul class="nav nav-pills nav-justified mb-4 pb-2">
            <li class="nav-item">
              <a class="nav-link" :class="{ 'active': role === 'student' }" href="#" @click.prevent="role = 'student'">Student</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" :class="{ 'active': role === 'company' }" href="#" @click.prevent="role = 'company'">Company</a>
            </li>
          </ul>
          
          <div v-if="error" class="alert alert-danger p-2 mb-3">{{ error }}</div>
          <div v-if="success" class="alert alert-success p-2 mb-3">{{ success }}</div>

          <!-- Student Registration Form -->
          <form v-if="role === 'student'" @submit.prevent="handleRegister">
            <div class="row">
               <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Full Name</label>
                <input type="text" class="form-control" v-model="student.full_name" required>
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Roll Number</label>
                <input type="text" class="form-control" v-model="student.roll_number" required>
              </div>
            </div>
            
            <div class="row">
               <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Branch</label>
                <input type="text" class="form-control" v-model="student.branch" required placeholder="e.g. CS">
              </div>
              <div class="col-md-6 mb-3">
                <label class="form-label fw-bold">Graduation Year</label>
                <input type="number" class="form-control" v-model="student.year" required>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold">CGPA</label>
              <input type="number" step="0.01" class="form-control" v-model="student.cgpa" required>
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold">Email</label>
              <input type="email" class="form-control" v-model="student.email" required>
            </div>
            <div class="mb-4">
              <label class="form-label fw-bold">Password</label>
              <input type="password" class="form-control" v-model="student.password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">Register as Student</button>
          </form>

          <!-- Company Registration Form -->
          <form v-if="role === 'company'" @submit.prevent="handleRegister">
             <div class="mb-3">
              <label class="form-label fw-bold">Company Name</label>
              <input type="text" class="form-control" v-model="company.company_name" required>
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold">HR Contact Name</label>
              <input type="text" class="form-control" v-model="company.hr_contact_name" required>
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold">Company Website</label>
              <input type="url" class="form-control" v-model="company.website" placeholder="https://...">
            </div>
            <div class="mb-3">
              <label class="form-label fw-bold">Email</label>
              <input type="email" class="form-control" v-model="company.email" required>
            </div>
            <div class="mb-4">
              <label class="form-label fw-bold">Password</label>
              <input type="password" class="form-control" v-model="company.password" required>
            </div>
            <button type="submit" class="btn btn-primary w-100" :disabled="loading">Register as Company</button>
          </form>

          <div class="text-center mt-4">
            <span>Already have an account?</span>
            <router-link to="/login" class="fw-bold ms-2 text-decoration-none">Login</router-link>
          </div>
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
      role: 'student',
      loading: false,
      error: '',
      success: '',
      student: { full_name: '', email: '', password: '', roll_number: '', branch: '', cgpa: null, year: null },
      company: { company_name: '', hr_contact_name: '', email: '', password: '', website: '' }
    }
  },
  methods: {
    async handleRegister() {
      this.loading = true;
      this.error = '';
      this.success = '';
      
      const endpoint = this.role === 'student' ? '/auth/student/register' : '/auth/company/register';
      const payload = this.role === 'student' ? this.student : this.company;

      try {
        const response = await api.post(endpoint, payload);
        this.success = response.data.message;
        
        // Clear forms
        if (this.role === 'student') {
          this.student = { full_name: '', email: '', password: '', roll_number: '', branch: '', cgpa: null, year: null };
        } else {
          this.company = { company_name: '', hr_contact_name: '', email: '', password: '', website: '' };
        }

        // Redirect to login after 2 seconds
        setTimeout(() => {
          this.$router.push('/login');
        }, 2000);

      } catch (err) {
        this.error = err.response?.data?.message || 'Registration failed. Please try again.';
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>
