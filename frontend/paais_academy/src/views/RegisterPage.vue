<template>
  <div class="register-page">
    <div class="container register-container">
      <div class="register-form">
        <div class="form-header">
          <h2>Join PAAIS Academy</h2>
          <p>Free access to world-class AI training</p>
        </div>

        <!-- Step 1: Enter Phone/Email -->
        <form v-if="!otpSent" @submit.prevent="sendOTP">
          <div class="mb-4">
            <label class="form-label">Phone or Email</label>
            <div class="input-group">
              <span class="input-group-text">
                <i class="fas fa-envelope"></i>
              </span>
              <input
                v-model="phoneOrEmail"
                type="text"
                class="form-control"
                placeholder="Your phone number or email"
                required
                @input="validateInput"
              />
            </div>
            <small v-if="inputError" class="text-danger">{{ inputError }}</small>
          </div>

          <button type="submit" class="btn btn-primary w-100 btn-lg" :disabled="isLoading">
            <span v-if="!isLoading">Get OTP</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm me-2"></span>
              Sending...
            </span>
          </button>

          <div class="divider my-4">Or</div>

          <p class="text-center text-muted">
            Already have an account?
            <router-link to="/login">Login here</router-link>
          </p>
        </form>

        <!-- Step 2: Verify OTP -->
        <form v-else @submit.prevent="verifyOTP">
          <div class="alert alert-info">
            <i class="fas fa-info-circle"></i>
            We sent an OTP to {{ phoneOrEmail }}
          </div>

          <div class="mb-4">
            <label class="form-label">Enter OTP</label>
            <div class="otp-inputs">
              <input
                v-for="(digit, index) in otpDigits"
                :key="index"
                v-model="otpDigits[index]"
                type="text"
                maxlength="1"
                class="otp-input"
                @input="focusNext(index)"
                @keydown="handleKeyDown($event, index)"
              />
            </div>
            <small class="text-muted d-block mt-2">
              <button type="button" class="btn btn-link btn-sm p-0" @click="resendOTP">
                Didn't get OTP? Resend
              </button>
            </small>
          </div>

          <div class="mb-4">
            <label class="form-label">Business Function (Optional)</label>
            <select v-model="businessFunction" class="form-select">
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

          <button
            type="submit"
            class="btn btn-primary w-100 btn-lg"
            :disabled="isLoading || otp.length < 6"
          >
            <span v-if="!isLoading">Complete Registration</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm me-2"></span>
              Creating account...
            </span>
          </button>

          <button
            type="button"
            class="btn btn-outline-secondary w-100 mt-2"
            @click="backToPhoneEntry"
          >
            Use different contact
          </button>
        </form>

        <div class="form-footer">
          <small class="text-muted">
            By registering, you agree to our
            <router-link to="/terms">Terms of Service</router-link> and
            <router-link to="/privacy">Privacy Policy</router-link>.
          </small>
        </div>
      </div>

      <!-- Features Sidebar -->
      <div class="register-features">
        <div class="feature-item">
          <div class="feature-number">1</div>
          <h4>Free Access</h4>
          <p>Learn without paying anything</p>
        </div>
        <div class="feature-item">
          <div class="feature-number">2</div>
          <h4>Learn AI Tools</h4>
          <p>ChatGPT, Claude, Gemini & more</p>
        </div>
        <div class="feature-item">
          <div class="feature-number">3</div>
          <h4>Get Certified</h4>
          <p>Earn recognized credentials</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/store'
import { useUIStore } from '../stores/store'
import apiClient from '../utils/api_client'

const router = useRouter()
const userStore = useUserStore()
const uiStore = useUIStore()

const phoneOrEmail = ref('')

const getErrorMessage = (error, fallback) =>
  error.response?.data?.detail ||
  error.response?.data?.error ||
  (typeof error.response?.data === 'string' ? error.response.data : null) ||
  fallback
const otpSent = ref(false)
const otpDigits = ref(['', '', '', '', '', ''])
const businessFunction = ref('')
const inputError = ref('')
const isLoading = ref(false)

const otp = computed(() => otpDigits.value.join(''))

const validateInput = () => {
  inputError.value = ''
  const email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const phone = /^\+?[1-9]\d{1,14}$/

  if (!phoneOrEmail.value) {
    inputError.value = 'Please enter your phone or email'
    return false
  }

  const isValidEmail = email.test(phoneOrEmail.value)
  const isValidPhone = phone.test(phoneOrEmail.value.replace(/\D/g, ''))

  if (!isValidEmail && !isValidPhone) {
    inputError.value = 'Please enter a valid phone number or email'
    return false
  }

  return true
}

const sendOTP = async () => {
  if (!validateInput()) return

  isLoading.value = true
  try {
    await apiClient.sendOTP(phoneOrEmail.value)
    otpSent.value = true
    uiStore.setSuccess('OTP sent! Check your phone/email')
  } catch (error) {
    const responseData = error.response?.data
    const message =
      responseData?.detail ||
      responseData?.error ||
      responseData?.contact?.[0] ||
      (typeof responseData === 'string' ? responseData : null) ||
      'Failed to send OTP'
    uiStore.setError(message)
  } finally {
    isLoading.value = false
  }
}

const focusNext = (index) => {
  if (otpDigits.value[index] && index < 5) {
    document.querySelectorAll('.otp-input')[index + 1]?.focus()
  }
}

const handleKeyDown = (event, index) => {
  if (event.key === 'Backspace' && !otpDigits.value[index] && index > 0) {
    document.querySelectorAll('.otp-input')[index - 1]?.focus()
  }
}

const resendOTP = async () => {
  isLoading.value = true
  try {
    await apiClient.sendOTP(phoneOrEmail.value)
    uiStore.setSuccess('OTP resent!')
  } catch (error) {
    uiStore.setError('Failed to resend OTP')
  } finally {
    isLoading.value = false
  }
}

const backToPhoneEntry = () => {
  otpSent.value = false
  otpDigits.value = ['', '', '', '', '', '']
  businessFunction.value = ''
}

const verifyOTP = async () => {
  if (otp.value.length < 6) {
    uiStore.setError('Please enter the complete OTP')
    return
  }

  isLoading.value = true
  try {
    const response = await apiClient.verifyOTP(phoneOrEmail.value, otp.value)

    const { access, refresh } = response.data
    const user = response.data.user || {
      id: response.data.user_id,
      username: response.data.username,
      email: response.data.email,
    }

    userStore.setTokens(access, refresh)
    userStore.setUser(user)

    // Update profile with business function
    if (businessFunction.value) {
      try {
        await apiClient.updateProfile({ business_function: businessFunction.value })
      } catch (error) {
        console.error('Failed to update profile:', error)
      }
    }

    uiStore.setSuccess('Welcome to PAAIS Academy!')
    await router.push({ name: 'Dashboard' })
  } catch (error) {
    const message = error.response?.data?.detail || 'Failed to verify OTP'
    uiStore.setError(message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  padding: 2rem 0;
  display: flex;
  align-items: center;
}

.register-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
}

.register-form {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.form-header {
  text-align: center;
  margin-bottom: 2rem;
}

.form-header h2 {
  color: var(--navy);
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.form-header p {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

.input-group-text {
  background: var(--lav);
  border: 1px solid var(--border-color);
  color: var(--secondary-color);
}

.form-control,
.form-select {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.form-control:focus,
.form-select:focus {
  border-color: var(--secondary-color);
  box-shadow: 0 0 0 3px rgba(233, 0, 255, 0.1);
}

.otp-inputs {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 0.5rem;
  padding: 0.75rem;
  border: 1px solid #d9d7e8;
  border-radius: 12px;
  background: #faf9ff;
}

.otp-input {
  width: 100%;
  height: 50px;
  border: 2px solid #b9b6cc;
  border-radius: 8px;
  background: #ffffff;
  color: var(--navy);
  text-align: center;
  font-size: 1.5rem;
  font-weight: bold;
  transition: all 0.2s ease;
}

.otp-input:focus {
  border-color: var(--secondary-color);
  box-shadow: 0 0 0 3px rgba(233, 0, 255, 0.1);
}

.otp-input:not(:empty) {
  border-color: var(--secondary-color);
}

.divider {
  text-align: center;
  position: relative;
  color: var(--text-secondary);
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--border-color);
  z-index: -1;
}

.divider span {
  background: white;
  padding: 0 1rem;
}

.form-footer {
  text-align: center;
  margin-top: 2rem;
}

.alert-info {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #1e3a8a;
  border-radius: 8px;
}

/* Features Sidebar */
.register-features {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.feature-item {
  color: white;
  text-align: center;
}

.feature-number {
  width: 50px;
  height: 50px;
  background: var(--secondary-color);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0 auto 1rem;
}

.feature-item h4 {
  color: white;
  font-size: 1.25rem;
  margin-bottom: 0.5rem;
}

.feature-item p {
  opacity: 0.8;
  font-size: 0.95rem;
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .register-container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .register-form {
    padding: 2rem;
  }

  .register-features {
    flex-direction: row;
    gap: 1rem;
  }

  .feature-item {
    text-align: left;
  }

  .otp-inputs {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
