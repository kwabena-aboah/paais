<template>
  <div class="lesson-view-page" v-if="lesson">
    <!-- Lesson Header -->
    <section class="lesson-header">
      <div class="container-fluid">
        <div class="header-content">
          <router-link :to="`/track/${trackId}`" class="back-link">
            <i class="fas fa-arrow-left"></i> Back to {{ trackName }}
          </router-link>
          <h1>{{ lesson.title }}</h1>
          <div class="lesson-stats">
            <span><i class="fas fa-clock"></i> {{ lesson.duration_minutes }} minutes</span>
            <span><i class="fas fa-layer-group"></i> {{ lesson.level }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Lesson Content -->
    <section class="lesson-content">
      <div class="container-fluid">
        <div class="row">
          <!-- Main Content -->
          <div class="col-lg-8">
            <div class="content-card">
              <!-- Video (if available) -->
              <div v-if="lesson.video_url" class="video-container mb-4">
                <div class="video-placeholder">
                  <i class="fas fa-play-circle"></i>
                  <p>Video content</p>
                  <a :href="lesson.video_url" target="_blank" class="btn btn-primary btn-sm">
                    Watch Video
                  </a>
                </div>
              </div>

              <!-- Lesson Content -->
              <div class="lesson-body">
                <div v-html="lesson.content_html" class="content-html"></div>

                <!-- AI Tools Covered -->
                <div
                  v-if="lesson.ai_tools_covered && lesson.ai_tools_covered.length > 0"
                  class="ai-tools-section mt-4"
                >
                  <h4>AI Tools Covered</h4>
                  <div class="tools-list">
                    <span v-for="tool in lesson.ai_tools_covered" :key="tool" class="tool-badge">
                      {{ tool }}
                    </span>
                  </div>
                </div>

                <!-- Sample Prompt -->
                <div v-if="lesson.sample_prompt" class="sample-prompt mt-4">
                  <h4>Try This Prompt</h4>
                  <div class="prompt-box">
                    <p>{{ lesson.sample_prompt }}</p>
                    <button @click="copyPrompt" class="btn btn-sm btn-outline-primary">
                      <i class="fas fa-copy"></i> Copy Prompt
                    </button>
                  </div>
                </div>
              </div>

              <!-- Quiz Section -->
              <div
                v-if="lesson.quiz_questions && lesson.quiz_questions.length > 0"
                class="quiz-section mt-5"
              >
                <h3>Lesson Quiz</h3>
                <p class="quiz-intro">Test your understanding of this lesson</p>

                <form @submit.prevent="submitQuiz" v-if="!quizSubmitted">
                  <div
                    v-for="(question, index) in lesson.quiz_questions"
                    :key="index"
                    class="question-item"
                  >
                    <h5>{{ index + 1 }}. {{ question.question }}</h5>
                    <div class="options">
                      <div
                        v-for="(option, optIndex) in question.options"
                        :key="optIndex"
                        class="form-check"
                      >
                        <input
                          type="radio"
                          :id="`q${index}o${optIndex}`"
                          :name="`question${index}`"
                          :value="optIndex"
                          v-model.number="quizAnswers[index]"
                          class="form-check-input"
                        />
                        <label :for="`q${index}o${optIndex}`" class="form-check-label">
                          {{ option }}
                        </label>
                      </div>
                    </div>
                  </div>

                  <button
                    type="submit"
                    class="btn btn-primary btn-lg mt-4"
                    :disabled="!allAnswersAnswered"
                  >
                    Submit Quiz
                  </button>
                </form>

                <!-- Quiz Results -->
                <div v-else class="quiz-results">
                  <div class="results-header" :class="{ passed: quizScore >= 70 }">
                    <h3 v-if="quizScore >= 70" class="text-success">
                      <i class="fas fa-check-circle"></i> Great Job!
                    </h3>
                    <h3 v-else class="text-warning"><i class="fas fa-redo"></i> Try Again</h3>
                    <p>You scored {{ quizScore }}%</p>
                  </div>

                  <div class="results-answers">
                    <div
                      v-for="(question, index) in lesson.quiz_questions"
                      :key="index"
                      class="answer-review"
                    >
                      <p class="question">{{ question.question }}</p>
                      <p
                        :class="
                          isAnswerCorrect(question, quizAnswers[index])
                            ? 'text-success'
                            : 'text-danger'
                        "
                      >
                        <strong>Your answer:</strong>
                        {{ question.options[quizAnswers[index]] }}
                      </p>
                      <p
                        v-if="!isAnswerCorrect(question, quizAnswers[index])"
                        class="text-success"
                      >
                        <strong>Correct answer:</strong>
                        {{ question.options[getCorrectAnswerIndex(question)] }}
                      </p>
                    </div>
                  </div>

                  <button
                    v-if="quizScore < 70"
                    @click="retakeQuiz"
                    class="btn btn-primary btn-lg mt-4"
                  >
                    Retake Quiz
                  </button>
                  <button
                    v-else
                    @click="completeLesson"
                    class="btn btn-success btn-lg mt-4"
                    :disabled="isLoading"
                  >
                    <span v-if="!isLoading">Complete Lesson</span>
                    <span v-else>
                      <span class="spinner-border spinner-border-sm me-2"></span>
                      Completing...
                    </span>
                  </button>
                </div>
              </div>

              <!-- No Quiz Section -->
              <div v-else class="complete-section mt-5">
                <button
                  @click="completeLesson"
                  class="btn btn-success btn-lg"
                  :disabled="isLoading"
                >
                  <span v-if="!isLoading">Mark as Complete</span>
                  <span v-else>
                    <span class="spinner-border spinner-border-sm me-2"></span>
                    Completing...
                  </span>
                </button>
              </div>
            </div>
          </div>

          <!-- Sidebar -->
          <div class="col-lg-4">
            <div class="sidebar-widget objectives-widget">
              <h5>Learning Objectives</h5>
              <ul class="objectives-list">
                <li v-for="objective in lesson.objectives" :key="objective">
                  <i class="fas fa-check"></i> {{ objective }}
                </li>
              </ul>
            </div>

            <div class="sidebar-widget progress-widget mt-4">
              <h5>Your Progress</h5>
              <div class="progress">
                <div class="progress-bar" :style="{ width: `${lessonProgress}%` }"></div>
              </div>
              <p class="mt-2 text-muted">{{ lessonProgress }}% complete</p>
            </div>

            <div class="sidebar-widget suggested-widget mt-4">
              <h5>Next Steps</h5>
              <p v-if="nextLesson" class="mb-3">After completing this lesson, try:</p>
              <router-link
                v-if="nextLesson"
                :to="`/track/${trackId}/lesson/${nextLesson.id}`"
                class="btn btn-outline-primary w-100"
              >
                Next Lesson: {{ nextLesson.title }}
              </router-link>
              <router-link v-else :to="`/track/${trackId}`" class="btn btn-outline-primary w-100">
                Back to Track
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
  <div v-else class="loading-page">
    <div class="spinner-border text-primary"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useCourseStore } from '../stores/store'
import { useUIStore } from '../stores/store'
import apiClient from '../utils/api_client'

const route = useRoute()
const courseStore = useCourseStore()
const uiStore = useUIStore()

const props = defineProps({
  trackId: String,
  lessonId: String,
})

const lesson = ref(null)
const trackName = ref('')
const quizAnswers = ref([])
const quizSubmitted = ref(false)
const quizScore = ref(0)
const isLoading = ref(false)
const lessonProgress = ref(0)

const allAnswersAnswered = computed(() => {
  if (!lesson.value || !Array.isArray(lesson.value.quiz_questions)) return true
  return (
    quizAnswers.value.length === lesson.value.quiz_questions.length &&
    quizAnswers.value.every((a) => a !== null && a !== undefined)
  )
})

const nextLesson = computed(() => {
  const allLessons = courseStore.getLessonsByTrack(props.trackId)
  const currentIndex = allLessons.findIndex((l) => String(l.id) === String(props.lessonId))
  return currentIndex >= 0 ? allLessons[currentIndex + 1] || null : null
})

const copyPrompt = () => {
  navigator.clipboard.writeText(lesson.value.sample_prompt)
  uiStore.setSuccess('Prompt copied to clipboard!')
}

const getCorrectAnswerIndex = (question) => {
  const correctAnswer = question.correct_answer ?? question.correct

  if (typeof correctAnswer === 'number') return correctAnswer

  if (typeof correctAnswer === 'string') {
    const trimmedAnswer = correctAnswer.trim()
    const numericIndex = Number(trimmedAnswer)

    if (Number.isInteger(numericIndex) && numericIndex >= 0) {
      return numericIndex
    }

    return question.options.findIndex(
      (option) => option.trim().toLowerCase() === trimmedAnswer.toLowerCase(),
    )
  }

  return -1
}

const isAnswerCorrect = (question, selectedAnswer) => {
  return getCorrectAnswerIndex(question) === Number(selectedAnswer)
}

const submitQuiz = async () => {
  isLoading.value = true
  try {
    const response = await apiClient.submitQuiz(props.lessonId, quizAnswers.value)
    quizScore.value = response.data.score
    quizSubmitted.value = true
    uiStore.setSuccess(
      response.data.passed
        ? 'Assessment passed! You can now complete this lesson.'
        : 'Assessment saved. Review the answers and try again to reach 70%.',
    )
  } catch (error) {
    uiStore.setError(error.response?.data?.error || 'Unable to submit assessment')
  } finally {
    isLoading.value = false
  }
}

const retakeQuiz = () => {
  quizAnswers.value = []
  quizSubmitted.value = false
  quizScore.value = 0
}

const completeLesson = async () => {
  isLoading.value = true
  try {
    await apiClient.completeLesson(props.lessonId, quizScore.value || null)
    uiStore.setSuccess('Lesson completed! Great work!')

    // Update progress
    courseStore.setLessonProgress(props.lessonId, {
      status: 'completed',
      progress_percentage: 100,
      quiz_score: quizScore.value,
      quiz_passed: quizScore.value >= 70,
    })

    lessonProgress.value = 100

    // Redirect to track after 2 seconds
    setTimeout(() => {
      window.location.href = `/track/${props.trackId}`
    }, 2000)
  } catch (error) {
    uiStore.setError('Failed to complete lesson')
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  try {
    const response = await apiClient.getLessonDetail(props.lessonId)
    lesson.value = response.data

    // Get track name
    const track = courseStore.getTrackById(props.trackId)
    trackName.value = track?.name || 'Track'

    // Initialize quiz answers
    if (lesson.value.quiz_questions) {
      quizAnswers.value = new Array(lesson.value.quiz_questions.length).fill(null)
    }

    // Start lesson
    await apiClient.startLesson(props.lessonId)
  } catch (error) {
    console.error('Failed to load lesson:', error)
  }
})
</script>

<style scoped>
.lesson-view-page {
  background: var(--lav);
  padding-top: 0px;
  padding-bottom: 4rem;
}

.lesson-header {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  color: white;
  padding: 3rem 0;
  margin-bottom: 2rem;
}

.header-content h1 {
  font-family: var(--font-poppins);
  font-size: 2.5rem;
  font-weight: 700;
  margin: 1rem 0;
}

.lesson-content {
  padding: 0px;
}

.lesson-stats {
  display: flex;
  gap: 2rem;
  opacity: 0.9;
}

.back-link {
  color: var(--cyan);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.back-link:hover {
  text-decoration: underline;
}

.content-card {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.video-container {
  position: relative;
  padding-bottom: 56.25%;
  height: 0;
  overflow: hidden;
  border-radius: 12px;
  background: var(--navy);
}

.video-placeholder {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
}

.video-placeholder i {
  font-size: 3rem;
  opacity: 0.5;
  margin-bottom: 1rem;
}

.content-html {
  color: var(--text-primary);
  line-height: 1.8;
}

.content-html h2,
.content-html h3 {
  margin-top: 2rem;
  margin-bottom: 1rem;
  color: var(--navy);
}

.content-html p {
  margin-bottom: 1rem;
}

.content-html ul,
.content-html ol {
  margin-left: 2rem;
  margin-bottom: 1rem;
}

.content-html li {
  margin-bottom: 0.5rem;
}

.content-html code {
  background: var(--lav);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: var(--secondary-color);
}

.content-html pre {
  background: var(--navy);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 1rem;
}

.ai-tools-section {
  border-top: 1px solid var(--border-color);
  padding-top: 2rem;
}

.ai-tools-section h4,
.sample-prompt h4 {
  color: var(--navy);
  margin-bottom: 1rem;
}

.tools-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tool-badge {
  display: inline-block;
  background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.sample-prompt {
  border-left: 4px solid var(--secondary-color);
  padding-left: 1.5rem;
}

.prompt-box {
  background: var(--lav);
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.prompt-box p {
  color: var(--text-primary);
  margin-bottom: 1rem;
  font-style: italic;
}

/* Quiz Section */
.quiz-section {
  border-top: 2px solid var(--border-color);
  padding-top: 2rem;
}

.quiz-section h3 {
  color: var(--navy);
}

.quiz-intro {
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.question-item {
  background: var(--lav);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.question-item h5 {
  color: var(--navy);
  margin-bottom: 1rem;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-check {
  display: flex;
  align-items: center;
}

.form-check-input {
  margin-right: 0.75rem;
  margin-top: 0;
}

.form-check-input:checked {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
}

.form-check-label {
  margin-bottom: 0;
  cursor: pointer;
}

.quiz-results {
  animation: slideUp 0.3s ease;
}

.results-header {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(46, 230, 214, 0.1));
  border: 2px solid rgba(16, 185, 129, 0.3);
  padding: 2rem;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 2rem;
}

.results-header h3 {
  margin: 0.5rem 0;
}

.results-header p {
  margin: 0;
  font-size: 2rem;
  font-weight: bold;
  color: var(--secondary-color);
}

.results-answers {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.answer-review {
  background: var(--lav);
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid var(--border-color);
}

.answer-review .question {
  color: var(--navy);
  font-weight: 600;
  margin-bottom: 1rem;
}

.answer-review p {
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}

/* Sidebar */
.sidebar-widget {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.sidebar-widget h5 {
  color: var(--navy);
  margin-bottom: 1rem;
  font-weight: 600;
}

.objectives-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.objectives-list li {
  padding: 0.5rem 0;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: var(--text-primary);
}

.objectives-list i {
  color: var(--secondary-color);
}

.progress-widget .progress {
  height: 8px;
}

.suggested-widget p {
  margin: 0;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.loading-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 500px;
  margin-top: 70px;
}
</style>
