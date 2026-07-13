<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Search Results for "{{ query }}"</h3>
      <router-link to="/admin" class="btn btn-outline-secondary">Back to Dashboard</router-link>
    </div>

    <!-- Matching Companies -->
    <div class="mb-5">
      <h5>Matching Companies</h5>
      <div class="card">
        <table class="table mb-0">
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th class="text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in companies" :key="company.id">
              <td>{{ company.name }}</td>
              <td>
                  <span v-if="company.is_active" class="text-success">Active</span>
                  <span v-else class="text-danger">Blacklisted</span>
              </td>
              <td class="text-center">
                <button class="btn btn-sm btn-primary" @click="viewCompany(company)">View</button>
              </td>
            </tr>
            <tr v-if="companies.length === 0"><td colspan="3" class="text-muted text-center py-3">No matching companies found</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Matching Students -->
    <div class="mb-5">
      <h5>Matching Students</h5>
      <div class="card">
        <table class="table mb-0">
          <thead>
            <tr>
              <th>Name</th>
              <th>Status</th>
              <th class="text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.id">
              <td>{{ student.name }}</td>
              <td>
                  <span v-if="student.is_active" class="text-success">Active</span>
                  <span v-else class="text-danger">Blacklisted</span>
              </td>
              <td class="text-center">
                <button class="btn btn-sm btn-primary" @click="viewStudent(student)">View</button>
              </td>
            </tr>
            <tr v-if="students.length === 0"><td colspan="3" class="text-muted text-center py-3">No matching students found</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <!-- Company Modal -->
    <div class="modal fade" id="companyModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedCompany">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedCompany.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
             <p><strong>HR Contact:</strong> {{ selectedCompany.contact || 'N/A' }}</p>
             <p><strong>Email:</strong> {{ selectedCompany.email }}</p>
             <p><strong>Website:</strong> {{ selectedCompany.website || 'N/A' }}</p>
             <p><strong>Status:</strong> {{ selectedCompany.is_active ? 'Active' : 'Blacklisted' }}</p>
          </div>
          <div class="modal-footer">
             <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Modal -->
    <div class="modal fade" id="studentSearchModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedStudent">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedStudent.name }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
             <p><strong>Roll Number:</strong> {{ selectedStudent.roll_number }}</p>
             <p><strong>Department:</strong> {{ selectedStudent.branch }}</p>
             <p><strong>Graduation Year:</strong> {{ selectedStudent.year }}</p>
             <p><strong>CGPA:</strong> {{ selectedStudent.cgpa }}</p>
             <p><strong>Status:</strong> {{ selectedStudent.is_active ? 'Active' : 'Blacklisted' }}</p>
          </div>
          <div class="modal-footer">
             <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import api from '../services/api';
import { Modal } from 'bootstrap';

export default {
  data() {
    return {
      query: '',
      companies: [],
      students: [],
      selectedCompany: null,
      selectedStudent: null,
      companyModalInstance: null,
      studentModalInstance: null
    }
  },
  watch: {
    '$route.query.q': {
      immediate: true,
      handler(newVal) {
        this.query = newVal || '';
        this.fetchResults();
      }
    }
  },
  mounted() {
    this.companyModalInstance = new Modal(document.getElementById('companyModal'));
    this.studentModalInstance = new Modal(document.getElementById('studentSearchModal'));
  },
  beforeUnmount() {
    if(this.companyModalInstance) this.companyModalInstance.dispose();
    if(this.studentModalInstance) this.studentModalInstance.dispose();
  },
  methods: {
    async fetchResults() {
      if (!this.query) return;
      try {
        const [comps, studs] = await Promise.all([
          api.get(`/admin/companies/registered?search=${this.query}`),
          api.get(`/admin/students?search=${this.query}`)
        ]);
        this.companies = comps.data;
        this.students = studs.data;
      } catch (error) {
        console.error("Error fetching search results:", error);
      }
    },
    viewCompany(company) {
      this.selectedCompany = company;
      this.companyModalInstance.show();
    },
    viewStudent(student) {
      this.selectedStudent = student;
      this.studentModalInstance.show();
    }
  }
}
</script>
