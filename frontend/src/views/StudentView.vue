<template>
  <div class="container py-4">
    <!-- Navbar -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="mb-0">Welcome {{ studentProfile.full_name || 'Student' }}</h4>
      <div>
        <button class="btn btn-sm btn-outline-primary" @click="openEditProfileModal">Edit Profile</button>
        <button class="btn btn-sm btn-outline-secondary ms-2" @click="openHistoryModal">History</button>
        <button class="btn btn-sm btn-danger ms-2" @click="logout">Logout</button>
      </div>
    </div>

    <div class="row">
      <!-- Left Panel -->
      <div class="col-md-5 mb-4">
        
        <!-- Organizations -->
        <h5>Organizations</h5>
        <div class="card p-3">
          <ul class="list-group list-group-flush" style="max-height: 400px; overflow-y: auto;">
            <li v-for="company in companies" :key="company.id" class="list-group-item d-flex justify-content-between align-items-center">
              {{ company.name }}
              <button class="btn btn-sm btn-primary" @click="openCompanyModal(company)">View Details</button>
            </li>
            <li v-if="companies.length === 0" class="list-group-item text-muted text-center">No organizations found</li>
          </ul>
        </div>

      </div>

      <!-- Right Panel -->
      <div class="col-md-7">
        <h5>My Applications</h5>
        <div class="card p-3 h-100">
          <div style="max-height: 600px; overflow-y: auto;">
            <table class="table mb-0">
              <thead>
                <tr>
                  <th>Company</th>
                  <th>Drive</th>
                  <th class="text-center">Status</th>
                  <th class="text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications" :key="app.id">
                  <td>{{ app.company }}</td>
                  <td>{{ app.title }}</td>
                  <td class="text-center">
                    <span class="badge bg-secondary">{{ app.status }}</span>
                  </td>
                  <td class="text-center">
                    <button class="btn btn-sm btn-primary" @click="viewAppliedDriveDetails(app)">View Details</button>
                    <button class="btn btn-sm btn-success ms-2 mt-2 mt-md-0" v-if="app.status === 'SHORTLISTED' && app.offered_dates && !app.selected_date" @click="openInterviewModal(app)">Schedule Interview</button>
                    <button class="btn btn-sm btn-info ms-2 mt-2 mt-md-0 text-white" v-if="app.status === 'INTERVIEW_SCHEDULED' && app.selected_date" @click="viewInterviewDetails(app)">Interview Details</button>
                  </td>
                </tr>
                <tr v-if="applications.length === 0">
                  <td colspan="4" class="text-center text-muted py-4">You haven't applied to any drives yet.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>


    <!-- Modals -->

    <!-- Company Details Modal -->
    <div class="modal fade" id="companyModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedCompany">
          <div class="modal-header">
             <h4 class="modal-title">{{ selectedCompany.name }}</h4>
             <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
            
            <h5>Overview</h5>
            <p class="small mb-4">{{ selectedCompany.description || 'No description available for this organization.' }}</p>

            <h5>Current Drives</h5>
            <div class="card p-2">
              <ul class="list-group list-group-flush" style="max-height: 300px; overflow-y: auto;">
                <li v-for="drive in getDrivesForCompany(selectedCompany.name)" :key="drive.id" class="list-group-item d-flex justify-content-between align-items-center">
                  {{ drive.title }}
                  <button class="btn btn-sm btn-primary" @click="openDriveDetailsFromCompany(drive)">View Details</button>
                </li>
                <li v-if="getDrivesForCompany(selectedCompany.name).length === 0" class="list-group-item text-muted text-center">No active drives available</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Profile Modal -->
    <div class="modal fade" id="editProfileModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Edit Profile</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
            <form @submit.prevent="updateProfile">
              <div class="mb-3">
                <label class="form-label small fw-bold">Full Name</label>
                <input type="text" class="form-control" v-model="editProfileData.full_name" required>
              </div>
              <div class="row mb-3">
                <div class="col-6">
                  <label class="form-label small fw-bold">Roll Number</label>
                  <input type="text" class="form-control" v-model="editProfileData.roll_number" required>
                </div>
                <div class="col-6">
                  <label class="form-label small fw-bold">Department</label>
                  <input type="text" class="form-control" v-model="editProfileData.branch" required>
                </div>
              </div>
              <div class="row mb-4">
                <div class="col-6">
                  <label class="form-label small fw-bold">CGPA</label>
                  <input type="number" step="0.1" class="form-control" v-model="editProfileData.cgpa" required>
                </div>
                <div class="col-6">
                  <label class="form-label small fw-bold">Graduation Year</label>
                  <input type="number" class="form-control" v-model="editProfileData.year" required>
                </div>
              </div>
              <div class="d-flex justify-content-end gap-2">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- History Modal -->
    <div class="modal fade" id="historyModal" tabindex="-1">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
             <h4 class="modal-title">Application History</h4>
             <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
             <div class="mb-4">
               <button class="btn btn-success btn-sm mb-3" @click="exportHistory">Export as CSV</button>
               <p class="mb-1 small">Student Name: {{ studentProfile.full_name }}</p>
               <p class="mb-0 small">Department: {{ studentProfile.branch }}</p>
             </div>

             <div class="card p-0">
               <div style="max-height: 400px; overflow-y: auto;">
                 <table class="table mb-0">
                   <thead>
                     <tr>
                       <th>Drive No.</th>
                       <th>Interview</th>
                       <th>Job Title</th>
                       <th>Results</th>
                       <th>Remark</th>
                     </tr>
                   </thead>
                   <tbody>
                     <tr v-for="(app, index) in applications" :key="app.id">
                       <td>{{ index + 1 }}.</td>
                       <td>In-person</td>
                       <td>{{ app.title }}</td>
                       <td>{{ app.status }}</td>
                       <td>None</td>
                     </tr>
                     <tr v-if="applications.length === 0">
                       <td colspan="5" class="text-center text-muted py-3">No application history</td>
                     </tr>
                   </tbody>
                 </table>
               </div>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Drive Details Modal -->
    <div class="modal fade" id="driveDetailsModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedDrive">
          <div class="modal-header">
            <h4 class="modal-title">Drive {{ selectedDrive.id }}</h4>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
             <div class="mb-4">
                 <p class="text-muted mb-1 small">Job Title</p>
                 <p class="fw-bold mb-3">{{ selectedDrive.title }}</p>
                 
                 <p class="text-muted mb-1 small">Job Description</p>
                 <p class="small mb-3">{{ selectedDrive.description }}</p>
                 
                 <p class="small mb-2">Salary: {{ selectedDrive.package }}</p>
                 <p class="small mb-3">Location: {{ selectedDrive.location }}</p>
             </div>
             
             <div class="d-flex gap-2 justify-content-start mt-4">
                <button class="btn btn-primary" @click="apply(selectedDrive.id)" v-if="!selectedDrive.applied && selectedDrive.is_eligible">Apply</button>
                <button class="btn btn-secondary" disabled v-if="selectedDrive.applied">Applied</button>
                <button class="btn btn-danger" disabled v-if="!selectedDrive.applied && !selectedDrive.is_eligible">Not Eligible</button>
                <button class="btn btn-outline-secondary" data-bs-dismiss="modal">Go Back</button>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Interview Scheduling Modal -->
    <div class="modal fade" id="interviewModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedInterviewApp">
          <div class="modal-header">
             <h4 class="modal-title">Schedule Interview</h4>
             <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4 text-center">
             <p class="text-muted small mb-3">Please select one of the interview slots offered by the company.</p>
             
             <div class="alert alert-info py-2 small mb-3 text-start" v-if="parsedInterviewSetup().mode">
                <strong>Mode:</strong> {{ parsedInterviewSetup().mode }} <br>
                <span v-if="parsedInterviewSetup().link"><strong>Location/Link:</strong> {{ parsedInterviewSetup().link }}</span>
             </div>
             
             <div class="d-flex flex-column gap-2 mb-4">
                <button class="btn btn-outline-primary" v-for="(date, i) in parsedInterviewSetup().dates" :key="i" @click="selectInterviewDate(date)">
                  {{ formatDateTime(date) }}
                </button>
             </div>
             <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- View Interview Details Modal -->
    <div class="modal fade" id="viewInterviewDetailsModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedInterviewApp">
          <div class="modal-header">
             <h4 class="modal-title">Interview Details</h4>
             <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body p-4">
             <p class="mb-2"><strong>Company:</strong> {{ selectedInterviewApp.company }}</p>
             <p class="mb-2"><strong>Role:</strong> {{ selectedInterviewApp.title }}</p>
             <p class="mb-4"><strong>Date:</strong> {{ formatDateTime(selectedInterviewApp.selected_date) }}</p>
             
             <div class="bg-light p-3 border mb-4">
                <p class="mb-2"><strong>Mode:</strong> {{ parsedInterviewSetup().mode || 'N/A' }}</p>
                <p class="mb-0"><strong>Location/Link:</strong> {{ parsedInterviewSetup().link || 'N/A' }}</p>
             </div>
             
             <div class="text-center">
                 <button class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
             </div>
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
      studentProfile: {},
      editProfileData: {},
      companies: [],
      drives: [],
      applications: [],
      selectedCompany: null,
      selectedDrive: null,
      companyModalInstance: null,
      editProfileModalInstance: null,
      historyModalInstance: null,
      driveDetailsModalInstance: null,
      selectedInterviewApp: null,
      interviewModalInstance: null,
      viewInterviewDetailsModalInstance: null
    }
  },
  mounted() {
    this.fetchData();
    this.companyModalInstance = new Modal(document.getElementById('companyModal'));
    this.editProfileModalInstance = new Modal(document.getElementById('editProfileModal'));
    this.historyModalInstance = new Modal(document.getElementById('historyModal'));
    this.driveDetailsModalInstance = new Modal(document.getElementById('driveDetailsModal'));
    this.interviewModalInstance = new Modal(document.getElementById('interviewModal'));
    this.viewInterviewDetailsModalInstance = new Modal(document.getElementById('viewInterviewDetailsModal'));
  },
  beforeUnmount() {
    if(this.companyModalInstance) this.companyModalInstance.dispose();
    if(this.editProfileModalInstance) this.editProfileModalInstance.dispose();
    if(this.historyModalInstance) this.historyModalInstance.dispose();
    if(this.driveDetailsModalInstance) this.driveDetailsModalInstance.dispose();
    if(this.interviewModalInstance) this.interviewModalInstance.dispose();
    if(this.viewInterviewDetailsModalInstance) this.viewInterviewDetailsModalInstance.dispose();
  },
  methods: {
    async fetchData() {
      try {
        const [profRes, compsRes, drivesRes, appsRes] = await Promise.all([
          api.get('/student/profile'),
          api.get('/student/companies'),
          api.get('/student/drives'),
          api.get('/student/applications')
        ]);
        this.studentProfile = profRes.data;
        this.companies = compsRes.data;
        this.drives = drivesRes.data;
        this.applications = appsRes.data;
      } catch (error) {
        console.error("Error fetching student data:", error);
      }
    },
    openCompanyModal(company) {
      this.selectedCompany = company;
      this.companyModalInstance.show();
    },
    getDrivesForCompany(companyName) {
      return this.drives.filter(d => d.company === companyName);
    },
    openEditProfileModal() {
      this.editProfileData = { ...this.studentProfile };
      this.editProfileModalInstance.show();
    },
    async updateProfile() {
      try {
        await api.patch('/student/profile', this.editProfileData);
        await this.fetchData();
        this.editProfileModalInstance.hide();
        alert('Profile updated successfully!');
      } catch (e) {
        alert('Failed to update profile.');
      }
    },
    openHistoryModal() {
      this.historyModalInstance.show();
    },
    async exportHistory() {
      try {
        const res = await api.get('/student/export-history', {
          responseType: 'blob' // Important to handle the binary file correctly
        });
        
        // Create a URL for the blob
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'application_history.csv');
        document.body.appendChild(link);
        link.click();
        
        // Clean up
        link.remove();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        alert('Failed to start export.');
      }
    },
    openDriveDetailsFromCompany(drive) {
      this.companyModalInstance.hide();
      this.selectedDrive = drive;
      this.driveDetailsModalInstance.show();
    },
    openInterviewModal(app) {
      this.selectedInterviewApp = app;
      this.interviewModalInstance.show();
    },
    viewInterviewDetails(app) {
      this.selectedInterviewApp = app;
      this.viewInterviewDetailsModalInstance.show();
    },
    parsedInterviewSetup() {
      if(!this.selectedInterviewApp || !this.selectedInterviewApp.offered_dates) return { dates: [] };
      try {
        const data = JSON.parse(this.selectedInterviewApp.offered_dates);
        if (Array.isArray(data)) {
           // Handle legacy data where only dates were stored
           return { dates: data, mode: null, link: null };
        }
        return data; // returns the { dates, mode, link } object
      } catch(e) { return { dates: [] }; }
    },
    formatDateTime(dateStr) {
      const d = new Date(dateStr);
      return d.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' });
    },
    async selectInterviewDate(dateStr) {
      if(!confirm("Are you sure you want to confirm this interview slot?")) return;
      try {
        await api.patch(`/student/applications/${this.selectedInterviewApp.id}/select_interview_date`, { selected_date: dateStr });
        alert('Interview scheduled successfully!');
        this.interviewModalInstance.hide();
        this.fetchData();
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to schedule interview.');
      }
    },
    openDriveDetails(drive) {
      this.selectedDrive = drive;
      this.driveDetailsModalInstance.show();
    },
    viewAppliedDriveDetails(app) {
      // Find the corresponding drive object from the applications drive_id
      const drive = this.drives.find(d => d.id === app.drive_id);
      if(drive) {
        this.openDriveDetails(drive);
      } else {
        // Fallback if drive not found in active drives (maybe it's closed)
        this.selectedDrive = {
           id: app.drive_id,
           title: app.title,
           description: app.drive_description || 'Description not available.',
           package: app.drive_package || 'N/A',
           location: app.drive_location || 'N/A',
           applied: true
        };
        this.driveDetailsModalInstance.show();
      }
    },
    async apply(driveId) {
      if (!confirm('Are you sure you want to apply for this role?')) return;
      try {
        await api.post(`/student/drives/${driveId}/apply`);
        alert('Application submitted successfully!');
        await this.fetchData();
        this.driveDetailsModalInstance.hide();
      } catch (err) {
        alert(err.response?.data?.message || 'Failed to apply.');
      }
    },
    formatDate(dateString) {
      if (!dateString) return 'N/A';
      return new Date(dateString).toLocaleDateString('en-GB'); // DD/MM/YYYY
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      this.$router.push('/login');
    }
  }
}
</script>

<style scoped>
body {
    background-color: #f9f9f9; 
}
.list-group-item:last-child {
  border-bottom: 0 !important;
}
.list-group-item:first-child {
  border-top: 0 !important;
}
</style>
