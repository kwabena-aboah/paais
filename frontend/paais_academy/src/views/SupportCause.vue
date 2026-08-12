<template>
  <div class="support-page container py-5">
    <div class="support-card">
      <span class="eyebrow">Keep learning free</span>
      <h1>Support the cause</h1>
      <p class="lead">PAAIS Academy keeps lessons and learning tracks free. If this work helps you, you can make an optional contribution of any amount.</p>

      <form v-if="!paymentStarted" class="support-form" @submit.prevent="startDonation">
        <label for="donationAmount" class="form-label">Donation amount (GHS)</label>
        <div class="input-group input-group-lg">
          <span class="input-group-text">GH₵</span>
          <input id="donationAmount" v-model="amount" class="form-control" type="number" min="1" step="0.01" placeholder="Any amount" required />
        </div>
        <label for="donationMessage" class="form-label mt-3">Optional message</label>
        <textarea id="donationMessage" v-model="message" class="form-control" rows="3" maxlength="500" placeholder="Tell us why you chose to support PAAIS"></textarea>
        <button class="btn btn-primary btn-lg w-100 mt-4" type="submit" :disabled="loading">
          {{ loading ? 'Preparing secure payment…' : 'Continue to secure payment' }}
        </button>
      </form>

      <div v-else class="success-state">
        <i class="bi bi-heart-fill"></i>
        <h2>Thank you for supporting free AI learning.</h2>
        <p>Complete the payment in the secure Paystack window. Your contribution will not unlock or restrict any lesson.</p>
        <a class="btn btn-primary" :href="authorizationUrl">Open secure payment</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import apiClient from '@/utils/api_client'
import { useUIStore } from '@/stores/store'

const route = useRoute()
const uiStore = useUIStore()
const amount = ref('')
const message = ref('')
const loading = ref(false)
const paymentStarted = ref(false)
const authorizationUrl = ref('')

const startDonation = async () => {
  loading.value = true
  try {
    const response = await apiClient.initializeDonation(amount.value, message.value)
    authorizationUrl.value = response.data.authorization_url
    paymentStarted.value = true
  } catch (error) {
    uiStore.setError(error.response?.data?.error || 'Unable to start the donation payment.')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  const reference = route.query.reference
  if (!reference || typeof reference !== 'string') return

  loading.value = true
  try {
    await apiClient.verifyDonation(reference)
    uiStore.setSuccess('Thank you. Your donation was received successfully.')
  } catch (error) {
    uiStore.setError('We could not confirm the donation yet. Please check your payment receipt.')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.support-page { min-height: 70vh; display: grid; place-items: center; background: var(--lav); }
.support-card { width: min(100%, 620px); padding: clamp(1.5rem, 5vw, 3rem); background: white; border: 1px solid var(--border-color); border-radius: 18px; box-shadow: 0 12px 30px rgba(10, 10, 51, .08); }
.support-card h1 { color: var(--navy); font-weight: 800; }
.support-card .lead { color: var(--text-secondary); }
.support-form { margin-top: 2rem; }
.input-group-text { color: var(--navy); background: var(--lav); border-color: var(--border-color); }
.success-state { padding-top: 2rem; text-align: center; }
.success-state > i { color: var(--secondary-color); font-size: 3rem; }
.success-state h2 { margin-top: 1rem; color: var(--navy); font-size: 1.35rem; }
.success-state p { color: var(--text-secondary); }
</style>
