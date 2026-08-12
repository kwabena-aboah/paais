<template>
  <div class="login-page">
    <div class="container login-container">
      <div class="login-form">
        <div class="form-header">
          <h2>Welcome Back</h2>
          <p>Continue your AI learning journey</p>
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
              />
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-100 btn-lg" :disabled="isLoading">
            <span v-if="!isLoading">Send OTP</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm me-2"></span>
              Sending...
            </span>
          </button>

          <p class="text-center text-muted mt-4">
            Don't have an account?
            <router-link to="/register">Register here</router-link>
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

          <button
            type="submit"
            class="btn btn-primary w-100 btn-lg"
            :disabled="isLoading || otp.length < 6"
          >
            <span v-if="!isLoading">Login</span>
            <span v-else>
              <span class="spinner-border spinner-border-sm me-2"></span>
              Logging in...
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
// import 'bootstrap/dist/css/bootstrap.min.css'
// import 'bootstrap'

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
const isLoading = ref(false)

const otp = computed(() => otpDigits.value.join(''))

const sendOTP = async () => {
  if (!phoneOrEmail.value) {
    uiStore.setError('Please enter your phone or email')
    return
  }

  isLoading.value = true
  try {
    await apiClient.sendOTP(phoneOrEmail.value, false)
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
    await apiClient.sendOTP(phoneOrEmail.value, false)
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

    uiStore.setSuccess('Login successful!')
    await router.push({ name: 'Dashboard' })
  } catch (error) {
    const message = error.response?.data?.detail || 'Failed to login'
    uiStore.setError(message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  padding: 2rem 0;
  display: flex;
  align-items: center;
}

.login-container {
  max-width: 400px;
  margin: 0 auto;
}

.login-form {
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

.form-control {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 0.75rem 1rem;
}

.form-control:focus {
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

.alert-info {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #1e3a8a;
  border-radius: 8px;
}

.text-center.text-muted {
  font-size: 0.95rem;
}

@media (max-width: 480px) {
  .login-form {
    padding: 2rem;
  }

  .otp-inputs {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
