<template>
  <div class="community-page container py-5">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div><span class="eyebrow">Learn together</span><h1>Community discussions</h1><p>Ask questions, share wins, and learn with other PAAIS learners.</p></div>
      <button class="btn btn-primary" @click="showComposer = !showComposer"><i class="bi bi-plus-lg me-2"></i>Start a discussion</button>
    </div>
    <form v-if="showComposer" class="composer-card mb-4" @submit.prevent="createPost">
      <input v-model="draft.title" class="form-control mb-3" placeholder="Discussion title" required />
      <textarea v-model="draft.body" class="form-control mb-3" rows="4" placeholder="What would you like to discuss?" required></textarea>
      <div class="d-flex gap-2"><button class="btn btn-primary" :disabled="saving">{{ saving ? 'Publishing…' : 'Publish discussion' }}</button><button type="button" class="btn btn-light" @click="showComposer = false">Cancel</button></div>
    </form>
    <div v-if="loading" class="text-center py-5">Loading discussions…</div>
    <article v-for="post in posts" v-else :key="post.id" class="post-card mb-3">
      <div class="d-flex justify-content-between gap-3"><div><h2>{{ post.title }}</h2><small>by {{ post.author_name || 'Learner' }} · {{ formatDate(post.created_at) }}</small></div><button class="like-button" :class="{ liked: post.liked_by_me }" @click="toggleLike(post)"><i class="bi bi-heart-fill"></i> {{ post.like_count }}</button></div>
      <p class="post-body">{{ post.body }}</p>
      <div class="comments"><div v-for="comment in post.comments" :key="comment.id" class="comment"><strong>{{ comment.author_name || 'Learner' }}</strong><span>{{ comment.body }}</span></div><form class="comment-form" @submit.prevent="commentOn(post)"><input v-model="commentDrafts[post.id]" class="form-control" placeholder="Add a helpful reply…" required /><button class="btn btn-sm btn-outline-primary">Reply</button></form></div>
    </article>
    <p v-if="!loading && !posts.length" class="empty-state">No discussions yet. Start the first one.</p>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import apiClient from '@/utils/api_client'
import { useUIStore } from '@/stores/store'

const uiStore = useUIStore()
const posts = ref([])
const loading = ref(true)
const saving = ref(false)
const showComposer = ref(false)
const draft = reactive({ title: '', body: '' })
const commentDrafts = reactive({})

const loadPosts = async () => {
  loading.value = true
  try { const response = await apiClient.getCommunityPosts(); posts.value = response.data.results ?? response.data } catch (error) { uiStore.setError('Unable to load community discussions.') } finally { loading.value = false }
}

const createPost = async () => {
  saving.value = true
  try { const response = await apiClient.createCommunityPost(draft); posts.value.unshift(response.data); draft.title = ''; draft.body = ''; showComposer.value = false; uiStore.setSuccess('Discussion published.') } catch (error) { uiStore.setError('Unable to publish your discussion.') } finally { saving.value = false }
}

const toggleLike = async (post) => { const response = await apiClient.toggleCommunityLike(post.id); post.liked_by_me = response.data.liked; post.like_count = response.data.like_count }
const commentOn = async (post) => { const body = commentDrafts[post.id]; if (!body) return; const response = await apiClient.addCommunityComment(post.id, body); post.comments.push(response.data); commentDrafts[post.id] = '' }
const formatDate = (value) => new Date(value).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
onMounted(loadPosts)
</script>

<style scoped>
.community-page { color: var(--ink); }
h1 { color: var(--navy); font-weight: 800; }
.eyebrow { color: var(--secondary-color); font-size: .75rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
.composer-card, .post-card { padding: 1.5rem; background: white; border: 1px solid var(--border-color); border-radius: 14px; box-shadow: 0 5px 18px rgba(10, 10, 51, .06); }
.post-card h2 { margin: 0 0 .25rem; color: var(--navy); font-size: 1.2rem; }
.post-card small, .post-body { color: var(--text-secondary); }
.post-body { margin: 1.25rem 0; white-space: pre-wrap; }
.like-button { border: 0; border-radius: 999px; padding: .45rem .75rem; color: var(--secondary-color); background: #fff1fc; }
.like-button.liked { color: white; background: var(--secondary-color); }
.comments { border-top: 1px solid var(--border-color); padding-top: 1rem; }
.comment { display: flex; gap: .5rem; margin-bottom: .65rem; font-size: .9rem; }
.comment strong { color: var(--navy); }
.comment span { color: var(--text-secondary); }
.comment-form { display: flex; gap: .5rem; margin-top: 1rem; }
.empty-state { padding: 4rem 0; color: var(--text-secondary); text-align: center; }
</style>
