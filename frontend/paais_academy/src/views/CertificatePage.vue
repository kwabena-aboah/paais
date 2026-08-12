<template>
  <div class="certificate-page">
    <section class="certificate-header">
      <div class="container-fluid">
        <h1>My Certificates</h1>
        <p>Track and verify your AI mastery credentials</p>
      </div>
    </section>

    <section class="certificate-content">
      <div class="container-fluid">
        <!-- Filter Tabs -->
        <div class="filter-tabs mb-4">
          <button
            v-for="level in ['all', 'starter', 'practitioner', 'champion']"
            :key="level"
            :class="['btn', activeFilter === level ? 'btn-primary' : 'btn-outline-primary']"
            @click="activeFilter = level"
          >
            {{ level === 'all' ? 'All Certificates' : formatLevel(level) }}
            <span class="badge" :class="activeFilter === level ? 'badge-light' : 'badge-primary'">
              {{ getCountByLevel(level) }}
            </span>
          </button>
        </div>

        <!-- Certificates Grid -->
        <div v-if="filteredCertificates.length > 0" class="row g-4">
          <div v-for="cert in filteredCertificates" :key="cert.id" class="col-lg-4 col-md-6">
            <div class="certificate-card" :class="`level-${cert.credential_type}`">
              <!-- Certificate Visual -->
              <div class="certificate-visual">
                <div class="cert-badge">
                  <i :class="getCertificateIcon(cert.credential_type)"></i>
                </div>
                <h4>{{ cert.track_name }}</h4>
                <p class="cert-level">{{ formatLevel(cert.credential_type) }}</p>
              </div>

              <!-- Certificate Details -->
              <div class="certificate-details">
                <div class="detail-row">
                  <span class="label">Credential #</span>
                  <span class="value">{{ cert.credential_number }}</span>
                </div>
                <div class="detail-row">
                  <span class="label">Issued</span>
                  <span class="value">{{ formatDate(cert.issued_at) }}</span>
                </div>
                <div v-if="cert.expires_at" class="detail-row">
                  <span class="label">Expires</span>
                  <span class="value">{{ formatDate(cert.expires_at) }}</span>
                </div>

                <div class="actions">
                  <button @click="verifyCertificate(cert)" class="btn btn-sm btn-outline-primary">
                    <i class="fas fa-check-circle"></i> Verify
                  </button>
                  <button
                    @click="downloadCertificate(cert)"
                    class="btn btn-sm btn-outline-secondary"
                  >
                    <i class="fas fa-download"></i> Download
                  </button>
                  <button
                    v-if="!cert.is_public"
                    @click="makeCertificatePublic(cert)"
                    class="btn btn-sm btn-outline-info"
                  >
                    <i class="fas fa-share"></i> Make Public
                  </button>
                  <span v-else class="badge badge-success">
                    <i class="fas fa-globe"></i> Public
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Empty State -->
        <div v-else class="empty-state">
          <div class="empty-icon">
            <i class="fas fa-certificate"></i>
          </div>
          <h3>No Certificates Yet</h3>
          <p>Complete courses to earn certificates and showcase your AI mastery</p>
          <router-link to="/dashboard" class="btn btn-primary"> Start Learning </router-link>
        </div>
      </div>
    </section>

    <!-- Verification Modal -->
    <div v-if="showVerificationModal" class="modal show d-block" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Verify Certificate</h5>
            <button type="button" class="btn-close" @click="showVerificationModal = false"></button>
          </div>
          <div class="modal-body">
            <p>Share this verification link with others to prove your credential:</p>
            <div class="input-group">
              <input type="text" class="form-control" :value="verificationLink" readonly />
              <button class="btn btn-primary" @click="copyVerificationLink">
                <i class="fas fa-copy"></i> Copy
              </button>
            </div>
            <small class="text-muted d-block mt-3">
              Verification Code: {{ selectedCertificate?.verification_code }}
            </small>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="showVerificationModal = false">
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showVerificationModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCourseStore } from '@/stores/store'
import { useUIStore } from '@/stores/store'
import apiClient from '@/utils/api_client'

const courseStore = useCourseStore()
const uiStore = useUIStore()

const activeFilter = ref('all')
const showVerificationModal = ref(false)
const selectedCertificate = ref(null)

const certificates = computed(() => {
  return Array.isArray(courseStore.certificates) ? courseStore.certificates : []
})

const filteredCertificates = computed(() => {
  if (activeFilter.value === 'all') return certificates.value
  return certificates.value.filter((c) => c.credential_type === activeFilter.value)
})

const verificationLink = computed(() => {
  if (!selectedCertificate.value) return ''
  return `${window.location.origin}/certificates/${selectedCertificate.value.id}/verify`
})

const formatLevel = (level) => {
  const mapping = {
    starter: 'AI Starter',
    practitioner: 'AI Practitioner',
    champion: 'AI Champion',
  }
  return mapping[level] || level
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

const getCertificateIcon = (level) => {
  const icons = {
    starter: 'fas fa-star',
    practitioner: 'fas fa-rocket',
    champion: 'fas fa-crown',
  }
  return icons[level] || 'fas fa-certificate'
}

const getCountByLevel = (level) => {
  return certificates.value.filter(
    cert => cert.credential_type === level
  ).length
}

const verifyCertificate = (cert) => {
  selectedCertificate.value = cert
  showVerificationModal.value = true
}

const copyVerificationLink = () => {
  navigator.clipboard.writeText(verificationLink.value)
  uiStore.setSuccess('Verification link copied!')
}

const downloadCertificate = (cert) => {
  // Generate PDF download (implementation depends on backend)
  uiStore.setSuccess('Certificate download started!')
}

const makeCertificatePublic = async (cert) => {
  try {
    await apiClient.makeCertificatePublic(cert.id)
    cert.is_public = true
    uiStore.setSuccess('Certificate is now public!')
  } catch (error) {
    uiStore.setError('Failed to update certificate')
  }
}

onMounted(async () => {
  try {
    const response = await apiClient.getCertificates()
    courseStore.setCertificates(
      response.data.results ?? response.data
    )
  } catch (error) {
    console.error('Failed to load certificates:', error)
  }
})
</script>

<style scoped>
.certificate-page {
  background: var(--lav);
  padding-top: 0px;
  padding-bottom: 4rem;
}

.certificate-header {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: white;
  padding: 3rem 0;
  margin-bottom: 3rem;
}

.certificate-header h1 {
  font-family: var(--font-poppins);
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.certificate-content {
  padding: 0px;
}

.filter-tabs {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-tabs .btn {
  border-radius: 20px;
  padding: 0.5rem 1.5rem;
  font-weight: 500;
}

.filter-tabs .badge {
  margin-left: 0.5rem;
}

/* Certificate Cards */
.certificate-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border-left: 6px solid var(--secondary-color);
  display: flex;
  flex-direction: column;
}

.certificate-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

.certificate-card.level-starter {
  border-left-color: #f59e0b;
}

.certificate-card.level-practitioner {
  border-left-color: var(--accent-color);
}

.certificate-card.level-champion {
  border-left-color: #fbbf24;
}

.certificate-visual {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.cert-badge {
  width: 80px;
  height: 80px;
  margin: 0 auto 1rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.certificate-visual h4 {
  color: white;
  margin-bottom: 0.5rem;
  font-size: 1.25rem;
}

.cert-level {
  opacity: 0.8;
  font-size: 0.9rem;
  margin: 0;
}

.certificate-details {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid var(--border-color);
}

.detail-row:last-of-type {
  margin-bottom: auto;
  border-bottom: none;
}

.detail-row .label {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.detail-row .value {
  color: var(--navy);
  font-weight: 600;
}

.actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.actions .btn {
  flex: 1;
  min-width: 100px;
  font-size: 0.85rem;
}

.actions .badge {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  color: var(--secondary-color);
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-state h3 {
  color: var(--navy);
  margin-bottom: 0.5rem;
}

.empty-state p {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

/* Modal */
.modal.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.modal-backdrop.show {
  background-color: rgba(0, 0, 0, 0.5);
}

.input-group {
  margin-bottom: 1rem;
}

.input-group .form-control {
  border-radius: 8px 0 0 8px;
}

.input-group .btn {
  border-radius: 0 8px 8px 0;
}

@media (max-width: 768px) {
  .filter-tabs {
    gap: 0.5rem;
  }

  .filter-tabs .btn {
    padding: 0.4rem 1rem;
    font-size: 0.9rem;
  }

  .actions {
    flex-direction: column;
  }

  .actions .btn {
    width: 100%;
    min-width: auto;
  }
}
</style>
