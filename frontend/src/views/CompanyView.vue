<template>
  <div class="container py-4">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="mb-0">Welcome {{ companyName }}</h2>
      <div class="d-flex gap-3">
        <button class="btn btn-outline-primary" @click="openProfileModal">Edit Profile</button>
        <button class="btn btn-danger" @click="logout">Logout</button>
      </div>
    </div>

    <!-- Alert if pending -->
    <div v-if="stats.status === 'PENDING'" class="alert alert-warning mb-4">
      Your company account is pending admin approval. You cannot create placement drives until approved.
    </div>

    <div class="row mb-4">
      <div class="col-md-4">
        <div class="card p-3 text-center">
          <h3>{{ stats.ongoing_drives || 0 }}</h3>
          <p class="text-muted mb-0">Ongoing Drives</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card p-3 text-center">
          <h3>{{ stats.closed_drives || 0 }}</h3>
          <p class="text-muted mb-0">Closed Drives</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card p-3 text-center">
          <h3>{{ stats.total_applicants_ongoing || 0 }}</h3>
          <p class="text-muted mb-0">Applicants in Ongoing Drives</p>
        </div>
      </div>
    </div>

    <div class="row">
      <!-- LEFT COLUMN: Create Drive Form -->
      <div class="col-md-5">
        <div class="card p-4">
          <h4 class="mb-4">Create a Drive</h4>
          <form @submit.prevent="createDrive">
            <div class="mb-3">
              <label class="form-label">Job Title</label>
              <input type="text" class="form-control" v-model="newDrive.title" required :disabled="stats.status !== 'APPROVED'">
            </div>
            <div class="mb-3">
              <label class="form-label">Description</label>
              <textarea class="form-control" rows="3" v-model="newDrive.job_description" required :disabled="stats.status !== 'APPROVED'"></textarea>
            </div>
            <div class="mb-3">
              <label class="form-label">Eligible Branches</label>
              <input type="text" class="form-control" v-model="newDrive.branch_eligibility" placeholder="e.g. CS, IT" required :disabled="stats.status !== 'APPROVED'">
            </div>
            <div class="row mb-3">
              <div class="col-6">
                <label class="form-label">Min CGPA</label>
                <input type="number" step="0.1" class="form-control" v-model="newDrive.minimum_cgpa" required :disabled="stats.status !== 'APPROVED'">
              </div>
              <div class="col-6">
                <label class="form-label">Target Year</label>
                <input type="number" class="form-control" v-model="newDrive.eligible_year" required :disabled="stats.status !== 'APPROVED'">
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Deadline</label>
              <input type="date" class="form-control" v-model="newDrive.application_deadline" required :disabled="stats.status !== 'APPROVED'">
            </div>
            <div class="mb-3">
              <label class="form-label">Location</label>
              <input type="text" class="form-control" v-model="newDrive.location" required :disabled="stats.status !== 'APPROVED'">
            </div>
            <div class="mb-4">
              <label class="form-label">Package Details</label>
              <input type="text" class="form-control" v-model="newDrive.package_details" required :disabled="stats.status !== 'APPROVED'">
            </div>
            <button class="btn btn-primary w-100" type="submit" :disabled="stats.status !== 'APPROVED'">Save</button>
          </form>
        </div>
      </div>
      
      <!-- RIGHT COLUMN: Lists -->
      <div class="col-md-7">
        <div class="card p-4" v-if="currentView === 'dashboard'">
          
          <h4 class="mb-4">Ongoing Drives</h4>
          <div v-if="upcomingDrives.length === 0" class="text-muted mb-4">No ongoing drives.</div>
          <div v-for="drive in upcomingDrives" :key="drive.id" class="card mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="card-title mb-0">{{ drive.title }}</h5>
                <span class="badge" :class="{'bg-warning text-dark': drive.status==='PENDING', 'bg-success': drive.status==='APPROVED'}">{{ drive.status }}</span>
              </div>
              <p class="text-muted small mb-3">Deadline: {{ new Date(drive.deadline).toLocaleDateString() }} | Location: {{ drive.location }}</p>
              
              <div class="d-flex gap-2">
                 <button class="btn btn-sm btn-primary" @click="viewApplicants(drive)">View Details</button>
                 <button class="btn btn-sm btn-success" @click="completeDrive(drive.id)">Mark as Complete</button>
              </div>
            </div>
          </div>
          
          <h4 class="mt-5 mb-4">Closed Drives</h4>
          <div v-if="closedDrives.length === 0" class="text-muted">No closed drives.</div>
          <div v-for="drive in closedDrives" :key="drive.id" class="card mb-3">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-center mb-2">
                <h5 class="card-title mb-0">{{ drive.title }}</h5>
                <span class="badge bg-danger" v-if="drive.status==='CANCELLED'">Cancelled</span>
                <span class="badge bg-secondary" v-else>Completed</span>
              </div>
              <p class="text-muted small mb-3">Location: {{ drive.location }}</p>
              
              <button class="btn btn-sm btn-primary" @click="openUpdateDriveModal(drive)">Update</button>
            </div>
          </div>
          
        </div>

        <div class="card p-4" v-else-if="currentView === 'applications'">
          <div class="d-flex justify-content-between align-items-center mb-4">
             <h4 class="mb-0">Update Applications</h4>
             <button class="btn btn-sm btn-outline-danger" @click="currentView = 'dashboard'">Back</button>
          </div>
          <p class="text-muted small mb-4">Job Title: {{ selectedDrive.title }}</p>
          
          <p class="fw-bold mb-3">Received Applications</p>
          <div class="card mb-2" v-for="app in applicants" :key="app.id">
            <div class="card-body py-3 d-flex justify-content-between align-items-center">
              <div>
                 <strong>{{ app.student_name }}</strong> 
                 <span class="badge bg-secondary ms-2" v-if="app.status !== 'APPLIED'">{{ app.status }}</span>
              </div>
              <button class="btn btn-sm btn-primary" @click="reviewApplication(app)">Review Application</button>
            </div>
          </div>
          <div v-if="applicants.length === 0" class="text-muted text-center py-4">No applications received yet.</div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    
    <!-- Student Application Modal -->
    <div class="modal fade" id="studentModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="selectedApplication">
          
          <!-- Resume Profile View -->
          <div class="modal-body p-4" v-if="showResume">
             <div class="mb-4 text-center">
                <h5 class="mb-1">{{ selectedApplication.student_name }}</h5>
                <p class="text-muted small">Student Profile</p>
             </div>
             
             <div class="bg-light p-3 rounded mb-4">
                 <p class="small mb-2"><strong>Roll Number:</strong> {{ selectedApplication.student_roll }}</p>
                 <p class="small mb-2"><strong>Department:</strong> {{ selectedApplication.student_branch }}</p>
                 <p class="small mb-2"><strong>Graduation Year:</strong> {{ selectedApplication.student_year }}</p>
                 <p class="small mb-2"><strong>CGPA:</strong> {{ selectedApplication.cgpa }}</p>
                 <p class="small mb-0"><strong>Email:</strong> {{ selectedApplication.student_email }}</p>
             </div>
             
             <button class="btn btn-outline-primary" @click="showResume = false">Back</button>
          </div>

          <!-- Application Status View -->
          <div class="modal-body p-4" v-else>
             <h5 class="mb-4">Student Application</h5>
             <div class="mb-4">
                 <p class="small mb-2"><strong>Student Name:</strong> {{ selectedApplication.student_name }}</p>
                 <p class="small mb-2"><strong>Department:</strong> {{ selectedApplication.student_branch }}</p>
                 <p class="small mb-2"><strong>Drive:</strong> {{ selectedDrive.title }}</p>
             </div>
             <div class="mt-4" v-if="draftStatus === 'SHORTLISTED'">
                 <label class="form-label small fw-bold mb-2">Offer 3 Interview Dates/Times</label>
                 <div class="d-flex flex-column gap-2 mb-3">
                   <input type="datetime-local" class="form-control form-control-sm" v-model="interviewSetup.dates[0]" required>
                   <input type="datetime-local" class="form-control form-control-sm" v-model="interviewSetup.dates[1]" required>
                   <input type="datetime-local" class="form-control form-control-sm" v-model="interviewSetup.dates[2]" required>
                 </div>
                 
                 <div class="row">
                   <div class="col-md-6 mb-3">
                     <label class="form-label small fw-bold mb-2">Interview Mode</label>
                     <select class="form-select form-select-sm" v-model="interviewSetup.mode">
                       <option value="VIRTUAL">Virtual</option>
                       <option value="IN-PERSON">In-person</option>
                     </select>
                   </div>
                   <div class="col-md-6 mb-3">
                     <label class="form-label small fw-bold mb-2">Meeting Link / Address</label>
                     <input type="text" class="form-control form-control-sm" v-model="interviewSetup.link" placeholder="Zoom link or office address">
                   </div>
                 </div>
             </div>
             
             <div class="d-flex justify-content-between align-items-center mt-3 pt-3 border-top">
                <button class="btn btn-outline-primary btn-sm" @click="showResume = true">View Resume</button>
                <div class="d-flex gap-2">
                  <select class="form-select form-select-sm" v-model="draftStatus">
                    <option value="APPLIED">Applied</option>
                    <option value="SHORTLISTED">Shortlist</option>
                    <option value="INTERVIEW_SCHEDULED">Waiting</option>
                    <option value="REJECTED">Reject</option>
                    <option value="SELECTED">Selected</option>
                  </select>
                  <button class="btn btn-success btn-sm" @click="saveStatus">Save</button>
                </div>
             </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Update Drive Modal -->
    <div class="modal fade" id="updateDriveModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content" v-if="updateDriveData">
          <div class="modal-header">
             <h5 class="modal-title">Update Drive</h5>
             <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
             <form @submit.prevent="updateDrive">
                <div class="mb-3">
                  <label class="form-label small fw-bold">Job Title</label>
                  <input type="text" class="form-control" v-model="updateDriveData.title" required>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Description</label>
                  <textarea class="form-control" rows="2" v-model="updateDriveData.job_description" required></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Eligible Branches</label>
                  <input type="text" class="form-control" v-model="updateDriveData.branch_eligibility" required>
                </div>
                <div class="row mb-3">
                  <div class="col-6">
                    <label class="form-label small fw-bold">Min CGPA</label>
                    <input type="number" step="0.1" class="form-control" v-model="updateDriveData.minimum_cgpa" required>
                  </div>
                  <div class="col-6">
                    <label class="form-label small fw-bold">Target Year</label>
                    <input type="number" class="form-control" v-model="updateDriveData.eligible_year" required>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Deadline</label>
                  <input type="date" class="form-control" v-model="updateDriveData.application_deadline" required>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Location</label>
                  <input type="text" class="form-control" v-model="updateDriveData.location" required>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Package Details</label>
                  <input type="text" class="form-control" v-model="updateDriveData.package_details" required>
                </div>
                <button class="btn btn-primary w-100 mt-2" type="submit">Update Drive</button>
             </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Company Profile Modal -->
    <div class="modal fade" id="companyProfileModal" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
             <h5 class="modal-title">Edit Company Profile</h5>
             <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
             <form @submit.prevent="updateProfile">
                <div class="mb-3">
                  <label class="form-label small fw-bold">Company Name</label>
                  <input type="text" class="form-control" v-model="profileData.company_name" required>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">HR Contact Name</label>
                  <input type="text" class="form-control" v-model="profileData.hr_contact_name" required>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">HR Email</label>
                  <input type="email" class="form-control" v-model="profileData.hr_email" required>
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Website</label>
                  <input type="text" class="form-control" v-model="profileData.website">
                </div>
                <div class="mb-3">
                  <label class="form-label small fw-bold">Description</label>
                  <textarea class="form-control" rows="3" v-model="profileData.description"></textarea>
                </div>
                <button class="btn btn-primary w-100 mt-2" type="submit">Save Profile</button>
             </form>
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
      companyName: localStorage.getItem('name') || 'Organization',
      stats: {},
      drives: [],
      currentView: 'dashboard',
      newDrive: {
        title: '', job_description: '', branch_eligibility: '', minimum_cgpa: '',
        eligible_year: '', application_deadline: '', location: '', package_details: ''
      },
      selectedDrive: null,
      applicants: [],
      selectedApplication: null,
      draftStatus: '',
      showResume: false,
      studentModalInstance: null,
      updateDriveModalInstance: null,
      updateDriveData: null,
      interviewSetup: { dates: ['', '', ''], mode: 'VIRTUAL', link: '' },
      profileData: { company_name: '', hr_contact_name: '', hr_email: '', website: '', description: '' },
      profileModalInstance: null
    }
  },
  computed: {
    upcomingDrives() {
      return this.drives.filter(d => d.status === 'APPROVED' || d.status === 'PENDING');
    },
    closedDrives() {
      return this.drives.filter(d => d.status === 'COMPLETED' || d.status === 'CANCELLED');
    }
  },
  mounted() {
    this.fetchData();
    this.studentModalInstance = new Modal(document.getElementById('studentModal'));
    this.updateDriveModalInstance = new Modal(document.getElementById('updateDriveModal'));
    this.profileModalInstance = new Modal(document.getElementById('companyProfileModal'));
  },
  beforeUnmount() {
    if(this.studentModalInstance) this.studentModalInstance.dispose();
    if(this.updateDriveModalInstance) this.updateDriveModalInstance.dispose();
    if(this.profileModalInstance) this.profileModalInstance.dispose();
  },
  methods: {
    async fetchData() {
      try {
        const [statsRes, drivesRes] = await Promise.all([
          api.get('/company/dashboard'),
          api.get('/company/drives')
        ]);
        this.stats = statsRes.data;
        this.drives = drivesRes.data;
      } catch (error) {
        console.error("Error fetching company data:", error);
      }
    },
    async createDrive() {
      try {
        await api.post('/company/drives', this.newDrive);
        this.newDrive = { title: '', job_description: '', branch_eligibility: '', minimum_cgpa: '', eligible_year: '', application_deadline: '', location: '', package_details: '' };
        this.fetchData();
        this.currentView = 'dashboard';
        alert('Drive created and pending admin approval.');
      } catch (err) {
        alert('Failed to create drive.');
      }
    },
    async viewApplicants(drive) {
      this.selectedDrive = drive;
      try {
        const res = await api.get(`/company/drives/${drive.id}/applications`);
        this.applicants = res.data;
        this.currentView = 'applications';
      } catch (err) {
        console.error("Error fetching applicants", err);
      }
    },
    async completeDrive(id) {
      if(!confirm("Are you sure you want to mark this drive as complete?")) return;
      try {
        await api.patch(`/company/drives/${id}/complete`);
        this.fetchData();
      } catch (e) {
        alert("Failed to complete drive");
      }
    },
    reviewApplication(app) {
      this.selectedApplication = app;
      this.draftStatus = app.status;
      this.interviewSetup = { dates: ['', '', ''], mode: 'VIRTUAL', link: '' };
      this.showResume = false;
      this.studentModalInstance.show();
    },
    async saveStatus() {
      if (!this.selectedApplication) return;
      if (this.draftStatus === 'SHORTLISTED') {
        if (!this.interviewSetup.dates[0] || !this.interviewSetup.dates[1] || !this.interviewSetup.dates[2]) {
          alert('Please select 3 interview dates.');
          return;
        }
      }
      
      try {
        const payload = { status: this.draftStatus };
        if (this.draftStatus === 'SHORTLISTED') {
          payload.offered_dates = this.interviewSetup;
        }
        await api.patch(`/company/applications/${this.selectedApplication.id}/status`, payload);
        this.selectedApplication.status = this.draftStatus;
        
        const idx = this.applicants.findIndex(a => a.id === this.selectedApplication.id);
        if (idx !== -1) this.applicants[idx].status = this.draftStatus;
        
        this.studentModalInstance.hide();
      } catch (err) {
        alert("Failed to update status.");
      }
    },
    openUpdateDriveModal(drive) {
      let formattedDate = '';
      if(drive.deadline) {
        const d = new Date(drive.deadline);
        if(!isNaN(d)) formattedDate = d.toISOString().split('T')[0];
      }
      this.updateDriveData = {
        id: drive.id,
        title: drive.title,
        job_description: drive.job_description || '',
        branch_eligibility: drive.branch_eligibility || '',
        minimum_cgpa: drive.minimum_cgpa || '',
        eligible_year: drive.eligible_year || '',
        application_deadline: formattedDate,
        location: drive.location || '',
        package_details: drive.package_details || ''
      };
      this.updateDriveModalInstance.show();
    },
    async updateDrive() {
      if (!this.updateDriveData) return;
      try {
        await api.patch(`/company/drives/${this.updateDriveData.id}`, this.updateDriveData);
        this.fetchData();
        this.updateDriveModalInstance.hide();
        alert('Drive updated and sent for admin approval.');
      } catch (e) {
        alert("Failed to update drive");
      }
    },
    async openProfileModal() {
      try {
        const res = await api.get('/company/profile');
        this.profileData = res.data;
        this.profileModalInstance.show();
      } catch (e) {
        alert("Failed to fetch profile");
      }
    },
    async updateProfile() {
      try {
        await api.patch('/company/profile', this.profileData);
        this.companyName = this.profileData.company_name;
        localStorage.setItem('name', this.companyName);
        this.profileModalInstance.hide();
        alert("Profile updated successfully!");
      } catch (e) {
        alert("Failed to update profile");
      }
    },
    logout() {
      localStorage.removeItem('token');
      localStorage.removeItem('role');
      localStorage.removeItem('name');
      this.$router.push('/login');
    }
  }
}
</script>
