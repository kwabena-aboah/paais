<template>
  <div class="profile-page">
    <section class="profile-header">
      <div class="container-fluid">
        <h1>My Profile</h1>
        <p>Manage your account and learning preferences</p>
      </div>
    </section>

    <section class="profile-content">
      <div class="container">
        <div class="row">
          <!-- Profile Form -->
          <div class="col-lg-8">
            <div class="card">
              <div class="card-header">
                <h5>Personal Information</h5>
              </div>
              <div class="card-body">
                <form @submit.prevent="updateProfile">
                  <div class="row">
                    <div class="col-md-6 mb-3">
                      <label class="form-label">First Name</label>
                      <input
                        v-model="formData.first_name"
                        type="text"
                        class="form-control"
                        placeholder="First name"
                      />
                    </div>
                    <div class="col-md-6 mb-3">
                      <label class="form-label">Last Name</label>
                      <input
                        v-model="formData.last_name"
                        type="text"
                        class="form-control"
                        placeholder="Last name"
                      />
                    </div>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Email</label>
                    <input
                      v-model="formData.email"
                      type="email"
                      class="form-control"
                      placeholder="Email address"
                    />
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Phone</label>
                    <input
                      v-model="formData.phone"
                      type="tel"
                      class="form-control"
                      placeholder="Phone number"
                      disabled
                    />
                    <small class="text-muted">Phone cannot be changed</small>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Business Function</label>
                    <select v-model="formData.business_function" class="form-select">
                      <option value="">Select your function</option>
                      <option value="marketing">Marketing</option>
                      <option value="sales">Sales</option>
                      <option value="finance">Finance</option>
                      <option value="hr">HR</option>
                      <option value="operations">Operations</option>
                      <option value="customer_service">Customer Service</option>
                      <option value="founder">Founder/SME</option>
                    </select>
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Company Name</label>
                    <input
                      v-model="formData.company_name"
                      type="text"
                      class="form-control"
                      placeholder="Your company"
                    />
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Country</label>
                    <input
                      v-model="formData.country"
                      type="text"
                      class="form-control"
                      placeholder="Your country"
                    />
                  </div>

                  <div class="mb-3">
                    <label class="form-label">Bio</label>
                    <textarea
                      v-model="formData.bio"
                      class="form-control"
                      placeholder="Tell us about yourself"
                      rows="4"
                    ></textarea>
                  </div>

                  <button type="submit" class="btn btn-primary" :disabled="isSaving">
                    <span v-if="!isSaving">Save Changes</span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      Saving...
                    </span>
                  </button>
                </form>
              </div>
            </div>

            <!-- Learning Preferences -->
            <div class="card mt-4">
              <div class="card-header">
                <h5>Learning Preferences</h5>
              </div>
              <div class="card-body">
                <div class="form-check mb-3">
                  <input
                    type="checkbox"
                    id="emailNotifications"
                    class="form-check-input"
                    v-model="formData.email_notifications"
                  />
                  <label class="form-check-label" for="emailNotifications">
                    Receive email notifications for new courses
                  </label>
                </div>

                <div class="form-check mb-3">
                  <input
                    type="checkbox"
                    id="marketingEmails"
                    class="form-check-input"
                    v-model="formData.marketing_emails"
                  />
                  <label class="form-check-label" for="marketingEmails">
                    Receive updates about new features and promotions
                  </label>
                </div>
              </div>
            </div>

            <!-- Danger Zone -->
            <div class="card mt-4 border-danger">
              <div class="card-header bg-danger bg-opacity-10">
                <h5 class="text-danger mb-0">Danger Zone</h5>
              </div>
              <div class="card-body">
                <p class="text-muted">
                  Once you delete your account, there is no going back. Please be certain.
                </p>
                <button class="btn btn-outline-danger" @click="showDeleteConfirm = true">
                  Delete My Account
                </button>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="col-lg-4">
            <!-- Account Summary -->
            <div class="card">
              <div class="card-header">
                <h5>Account Summary</h5>
              </div>
              <div class="card-body">
                <div class="summary-item">
                  <label>Member Since</label>
                  <p>{{ formatDate(userProfile?.user?.date_joined) }}</p>
                </div>
                <div class="summary-item">
                  <label>Account Status</label>
                  <p>
                    <span
                      class="badge"
                      :class="userProfile?.account_status === 'Active' ? 'badge-success' : 'badge-warning'"
                    >
                      {{ userProfile?.account_status || 'Unknown' }}
                    </span>
                  </p>
                </div>
                <div class="summary-item">
                  <label>Verified</label>
                  <p>
                    <span v-if="userProfile?.is_verified" class="badge badge-success">
                      <i class="fas fa-check"></i> Verified
                    </span>
                    <span v-else class="badge badge-warning">Not Verified</span>
                  </p>
                </div>
              </div>
            </div>

            <!-- Quick Stats -->
            <div class="card mt-4">
              <div class="card-header">
                <h5>Quick Stats</h5>
              </div>
              <div class="card-body">
                <div class="stat-item">
                  <i class="fas fa-book-open"></i>
                  <div>
                    <span class="stat-number">{{ userProfile?.courses_started || 0 }}</span>
                    <span class="stat-label">Courses Started</span>
                  </div>
                </div>
                <div class="stat-item">
                  <i class="fas fa-check-circle"></i>
                  <div>
                    <span class="stat-number">{{ userProfile?.courses_completed || 0 }}</span>
                    <span class="stat-label">Courses Completed</span>
                  </div>
                </div>
                <div class="stat-item">
                  <i class="fas fa-certificate"></i>
                  <div>
                    <span class="stat-number">{{ userProfile?.certificates_earned || 0 }}</span>
                    <span class="stat-label">Certificates Earned</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="modal show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Delete Account</h5>
            <button type="button" class="btn-close" @click="showDeleteConfirm = false"></button>
          </div>
          <div class="modal-body">
            <p class="text-danger">
              <strong>Warning:</strong> This action cannot be undone. All your data will be
              permanently deleted.
            </p>
            <p>Type "DELETE" to confirm:</p>
            <input
              v-model="deleteConfirmText"
              type="text"
              class="form-control"
              placeholder="Type DELETE to confirm"
            />
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showDeleteConfirm = false">
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-danger"
              @click="deleteAccount"
              :disabled="deleteConfirmText !== 'DELETE'"
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showDeleteConfirm" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/store'
import { useUIStore } from '../stores/store'
import apiClient from '../utils/api_client'

const router = useRouter()
const userStore = useUserStore()
const uiStore = useUIStore()

const formData = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  business_function: '',
  company_name: '',
  country: '',
  bio: '',
  email_notifications: true,
  marketing_emails: false,
})

const userProfile = computed(() => userStore.profile)
const isSaving = ref(false)
const showDeleteConfirm = ref(false)
const deleteConfirmText = ref('')

const formatDate = (date) => {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const updateProfile = async () => {
  isSaving.value = true
  try {
    await apiClient.updateProfile({
      first_name: formData.value.first_name,
      last_name: formData.value.last_name,
      email: formData.value.email,
      // Phone is read-only and must not be submitted as part of profile updates.
      business_function: formData.value.business_function,
      company_name: formData.value.company_name,
      country: formData.value.country,
      bio: formData.value.bio,
      email_notifications: formData.value.email_notifications,
      marketing_consent: formData.value.marketing_emails,
    })
    const profileResponse = await apiClient.getProfile()
    userStore.setProfile(profileResponse.data)
    uiStore.setSuccess('Profile updated successfully!')
  } catch (error) {
    uiStore.setError(
      error.response?.data?.phone?.[0] ||
      error.response?.data?.detail ||
      'Failed to update profile. Please check your details and try again.',
    )
  } finally {
    isSaving.value = false
  }
}

const deleteAccount = async () => {
  try {
    await apiClient.deleteProfile()

    userStore.logout()
    uiStore.setSuccess('Account deleted successfully')
    await router.push({ name: 'Home' })
  } catch (error) {
    uiStore.setError(
      error.response?.data?.detail ||
      'Failed to delete account. Please try again.',
    )
  }
}

onMounted(async () => {
  try {
    const response = await apiClient.getProfile()
    const profile = response.data
    userStore.setProfile(profile)

    const currentUser = profile.user || userStore.user || {}
    formData.value = {
      first_name: currentUser.first_name || '',
      last_name: currentUser.last_name || '',
      email: currentUser.email || '',
      phone: profile.phone || '',
      business_function: profile.business_function || '',
      company_name: profile.company_name || '',
      country: profile.country || '',
      bio: profile.bio || '',
      email_notifications: profile.email_notifications !== false,
      marketing_emails: profile.marketing_consent || false,
    }
  } catch (error) {
    console.error('Failed to load profile:', error)
  }
})
</script>

<style scoped>
.profile-page {
  background: var(--lav);
  padding-top: 0px;
  padding-bottom: 4rem;
}

.profile-header {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: white;
  padding: 3rem 0;
  margin-bottom: 3rem;
}

.profile-header h1 {
  font-family: var(--font-poppins);
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.profile-content {
  padding: 0;
}

.card {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 2rem;
}

.card-header {
  background: var(--lav);
  border-bottom: 1px solid var(--border-color);
  padding: 1.5rem;
}

.card-header h5 {
  margin: 0;
  color: var(--navy);
  font-weight: 600;
}

.card-body {
  padding: 2rem;
}

.form-control,
.form-select {
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.form-control:focus,
.form-select:focus {
  border-color: var(--secondary-color);
  box-shadow: 0 0 0 3px rgba(233, 0, 255, 0.1);
}

.form-check {
  padding-left: 0;
  margin-bottom: 1rem;
}

.form-check-input {
  margin-right: 0.75rem;
}

.summary-item {
  margin-bottom: 1.5rem;
}

.summary-item label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.85rem;
  text-transform: uppercase;
}

.summary-item p {
  margin: 0.5rem 0 0 0;
  color: var(--navy);
  font-size: 1.1rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-item i {
  font-size: 1.5rem;
  color: var(--secondary-color);
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--navy);
}

.stat-label {
  display: block;
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.border-danger {
  border-color: #ef4444 !important;
}

.bg-danger.bg-opacity-10 {
  background-color: rgba(239, 68, 68, 0.1) !important;
}

.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-backdrop {
  background-color: rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .profile-header h1 {
    font-size: 1.5rem;
  }
}
</style>
