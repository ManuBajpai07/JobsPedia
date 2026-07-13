<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">Welcome Admin</h3>
      <button class="btn btn-sm btn-outline-danger" @click="logout">Logout</button>
    </div>

    <!-- Registered Companies -->
    <div class="mb-4">
      <h5>Registered Companies</h5>
      <div class="card">
        <ul class="list-group list-group-flush">
          <li v-for="company in registeredCompanies" :key="company.id" class="list-group-item d-flex justify-content-between align-items-center">
            {{ company.name }}
            <div>
              <button class="btn btn-sm btn-outline-danger me-2" @click="toggleUserStatus(company.user_id)" v-if="company.is_active">Blacklist</button>
              <button class="btn btn-sm btn-outline-success me-2" @click="toggleUserStatus(company.user_id)" v-else>Whitelist</button>
              <button class="btn btn-sm btn-danger" @click="deleteUser(company.user_id)">Delete</button>
            </div>
          </li>
          <li v-if="registeredCompanies.length === 0" class="list-group-item text-muted text-center">No companies found</li>
        </ul>
      </div>
    </div>

    <!-- Registered Students -->
    <div class="mb-4">
      <h5>Registered Students</h5>
      <div class="card">
        <ul class="list-group list-group-flush">
          <li v-for="student in students" :key="student.id" class="list-group-item d-flex justify-content-between align-items-center">
            {{ student.name }}
            <div>
              <button class="btn btn-sm btn-outline-danger me-2" @click="toggleUserStatus(student.user_id)" v-if="student.is_active">Blacklist</button>
              <button class="btn btn-sm btn-outline-success me-2" @click="toggleUserStatus(student.user_id)" v-else>Whitelist</button>
              <button class="btn btn-sm btn-danger" @click="deleteUser(student.user_id)">Delete</button>
            </div>
          </li>
          <li v-if="students.length === 0" class="list-group-item text-muted text-center">No students found</li>
        </ul>
      </div>
    </div>

    <!-- Company Applications -->
    <div class="mb-4">
      <h5>Company Applications</h5>
      <div class="card">
        <ul class="list-group list-group-flush">
          <li v-for="company in pendingCompanies" :key="company.id" class="list-group-item d-flex justify-content-between align-items-center">
            {{ company.name }}
            <button class="btn btn-sm btn-success" @click="approveCompany(company.id)">Approve</button>
          </li>
          <li v-if="pendingCompanies.length === 0" class="list-group-item text-muted text-center">No pending applications</li>
        </ul>
      </div>
    </div>

    <!-- Pending Placement Drives -->
    <div class="mb-4">
      <h5>Pending Placement Drives</h5>
      <div class="card">
        <table class="table mb-0">
          <thead>
            <tr>
              <th>Company</th>
              <th>Drive Name</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="drive in pendingDrives" :key="drive.id">
              <td>{{ drive.company }}</td>
              <td>{{ drive.title }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-danger me-2" @click="rejectDrive(drive.id)">Reject</button>
                <button class="btn btn-sm btn-success" @click="approveDrive(drive.id)">Approve</button>
              </td>
            </tr>
            <tr v-if="pendingDrives.length === 0"><td colspan="3" class="text-muted text-center py-3">No pending drives</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Ongoing Drives -->
    <div class="mb-4">
      <h5>Ongoing Drives</h5>
      <div class="card">
        <table class="table mb-0">
          <thead>
            <tr>
              <th>Sr No.</th>
              <th>Drive Name</th>
              <th class="text-end">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(drive, index) in ongoingDrives" :key="drive.id">
              <td>{{ index + 1001 }}.</td>
              <td>{{ drive.title }}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-primary me-2" @click="viewDrive(drive)">View Details</button>
                <button class="btn btn-sm btn-success" @click="completeDrive(drive.id)">Mark as Complete</button>
              </td>
            </tr>
            <tr v-if="ongoingDrives.length === 0"><td colspan="3" class="text-muted text-center py-3">No ongoing drives</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Student Applications -->
    <div class="mb-5">
      <h5>Student Applications</h5>
      <div class="card">
        <table class="table mb-0">
          <thead>
            <tr>
              <th>Sr No.</th>
              <th>Name</th>
              <th>Drive</th>
              <th>Company</th>
              <th>Date</th>
              <th class="text-center">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(app, index) in studentApplications" :key="app.id">
              <td>{{ index + 1 }}.</td>
              <td>{{ app.student_name }}</td>
              <td>{{ app.drive_title }}</td>
              <td>{{ app.company_name }}</td>
              <td>{{ app.date }}</td>
              <td class="text-center">
                <button class="btn btn-sm btn-primary" @click="viewStudent(app)">View</button>
              </td>
            </tr>
            <tr v-if="studentApplications.length === 0"><td colspan="6" class="text-muted text-center py-3">No applications</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modals -->
    <!-- Drive Modal -->
    <div class="modal fade" id="driveModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedDrive">
          <div class="modal-header">
            <h5 class="modal-title">{{ selectedDrive.company }} - {{ selectedDrive.title }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
             <div class="mb-4">
                 <p><strong>Job Description:</strong> {{ selectedDrive.description }}</p>
                 <p><strong>Salary:</strong> {{ selectedDrive.salary }}</p>
                 <p><strong>Location:</strong> {{ selectedDrive.location }}</p>
             </div>
             
             <h5>Applicants</h5>
             <div class="card">
               <div style="max-height: 250px; overflow-y: auto;">
                 <table class="table mb-0">
                   <thead>
                     <tr>
                       <th>Name</th>
                       <th>Dept</th>
                       <th>Status</th>
                       <th>Action</th>
                     </tr>
                   </thead>
                   <tbody>
                     <tr v-for="app in selectedDriveApplications" :key="app.id">
                       <td>{{ app.student_name }}</td>
                       <td>{{ app.student_branch }}</td>
                       <td>
                         <span class="badge bg-secondary">{{ app.status }}</span>
                       </td>
                       <td>
                         <button class="btn btn-sm btn-primary" @click="viewStudentResumeFromDrive(app)">View Resume</button>
                       </td>
                     </tr>
                     <tr v-if="selectedDriveApplications.length === 0">
                       <td colspan="4" class="text-center text-muted py-3">No applications yet.</td>
                     </tr>
                   </tbody>
                 </table>
               </div>
             </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" data-bs-dismiss="modal">Go Back</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Student Modal -->
    <div class="modal fade" id="studentModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedStudent">
          <div class="modal-header">
             <h5 class="modal-title">Student Application</h5>
             <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="showResume">
             <h5 class="mb-3">{{ selectedStudent.student_name }} - Profile</h5>
             <p><strong>Roll Number:</strong> {{ selectedStudent.student_roll }}</p>
             <p><strong>Department:</strong> {{ selectedStudent.student_branch }}</p>
             <p><strong>Graduation Year:</strong> {{ selectedStudent.student_year }}</p>
             <p><strong>CGPA:</strong> {{ selectedStudent.student_cgpa }}</p>
             <p><strong>Status:</strong> {{ selectedStudent.student_is_active ? 'Active' : 'Blacklisted' }}</p>
          </div>
          <div class="modal-body" v-else>
             <p><strong>Student Name:</strong> {{ selectedStudent.student_name }}</p>
             <p><strong>Department:</strong> {{ selectedStudent.student_branch }}</p>
             <p><strong>Drive:</strong> {{ selectedStudent.drive_title }}</p>
          </div>
          <div class="modal-footer">
             <button class="btn btn-primary" v-if="!showResume" @click="showResume = true">View Resume</button>
             <button class="btn btn-secondary" v-if="showResume" @click="handleResumeBack">Back</button>
             <button class="btn btn-secondary" v-if="!showResume" data-bs-dismiss="modal">Close</button>
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
      registeredCompanies: [],
      students: [],
      pendingCompanies: [],
      pendingDrives: [],
      ongoingDrives: [],
      studentApplications: [],
      selectedDrive: null,
      selectedDriveApplications: [],
      selectedStudent: null,
      openedFromDriveModal: false,
      showResume: false,
      driveModalInstance: null,
      studentModalInstance: null
    }
  },
  mounted() {
    this.fetchData();
    this.driveModalInstance = new Modal(document.getElementById('driveModal'));
    this.studentModalInstance = new Modal(document.getElementById('studentModal'));
  },
  beforeUnmount() {
    if(this.driveModalInstance) this.driveModalInstance.dispose();
    if(this.studentModalInstance) this.studentModalInstance.dispose();
  },
  methods: {
    async fetchData() {
      try {
        const [regComp, pendComp, studs, pendDrives, drives, apps] = await Promise.all([
          api.get(`/admin/companies/registered`),
          api.get('/admin/companies/pending'),
          api.get(`/admin/students`),
          api.get('/admin/drives/pending'),
          api.get('/admin/drives/ongoing'),
          api.get('/admin/applications')
        ]);
        this.registeredCompanies = regComp.data;
        this.pendingCompanies = pendComp.data;
        this.students = studs.data;
        this.pendingDrives = pendDrives.data;
        this.ongoingDrives = drives.data;
        this.studentApplications = apps.data;
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    },
    async toggleUserStatus(userId) {
      try {
        await api.patch(`/admin/users/${userId}/toggle_status`);
        this.fetchData();
      } catch (e) {
        alert("Failed to toggle status");
      }
    },
    async approveCompany(id) {
      try {
        await api.patch(`/admin/companies/${id}/approve`);
        this.fetchData();
      } catch (e) {
        alert("Failed to approve company");
      }
    },
    async approveDrive(id) {
      try {
        await api.patch(`/admin/drives/${id}/approve`);
        this.fetchData();
      } catch (e) {
        alert("Failed to approve drive");
      }
    },
    async rejectDrive(id) {
      if(!confirm("Are you sure you want to reject this drive?")) return;
      try {
        await api.patch(`/admin/drives/${id}/reject`);
        this.fetchData();
      } catch (e) {
        alert("Failed to reject drive");
      }
    },
    async deleteUser(id) {
      if(!confirm("Are you sure you want to permanently delete this user and all associated data? This action cannot be undone.")) return;
      try {
        await api.delete(`/admin/users/${id}`);
        this.fetchData();
      } catch (e) {
        alert("Failed to delete user");
      }
    },
    async completeDrive(id) {
      if(!confirm("Are you sure you want to mark this drive as complete?")) return;
      try {
        await api.patch(`/admin/drives/${id}/complete`);
        this.fetchData();
      } catch (e) {
        alert("Failed to complete drive");
      }
    },
    viewDrive(drive) {
      this.selectedDrive = drive;
      this.selectedDriveApplications = [];
      this.driveModalInstance.show();
      this.fetchDriveApplications(drive.id);
    },
    async fetchDriveApplications(id) {
      try {
        const res = await api.get(`/admin/drives/${id}/applications`);
        this.selectedDriveApplications = res.data;
      } catch (err) {
        console.error("Failed to fetch applications for drive");
      }
    },
    viewStudentResumeFromDrive(app) {
      this.driveModalInstance.hide();
      this.selectedStudent = app;
      this.showResume = true;
      this.openedFromDriveModal = true;
      this.studentModalInstance.show();
    },
    viewStudent(app) {
      this.selectedStudent = app;
      this.showResume = false;
      this.openedFromDriveModal = false;
      this.studentModalInstance.show();
    },
    handleResumeBack() {
      if (this.openedFromDriveModal) {
        this.studentModalInstance.hide();
        this.driveModalInstance.show();
      } else {
        this.showResume = false;
      }
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      this.$router.push('/login');
    }
  }
}
</script>
