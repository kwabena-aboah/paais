import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/store'

// Lazy-loaded components
const HomePage = () => import('../views/HomePage.vue')
const RegisterPage = () => import('../views/RegisterPage.vue')
const LoginPage = () => import('../views/LoginPage.vue')
const TermsOfService = () => import('../views/TermsOfService.vue')
const PrivacyPolicy = () => import('../views/PrivacyPolicy.vue')
const Dashboard = () => import('../views/Dashboard.vue')
const AvailableTracks = () => import('../views/AvailableTracks.vue')
const TrackDetail = () => import('../views/TrackDetail.vue')
const LessonView = () => import('../views/LessonView.vue')
const ProfilePage = () => import('../views/ProfilePage.vue')
const CertificatePage = () => import('../views/CertificatePage.vue')
const AdminPanel = () => import('../views/AdminPanel.vue')
const Community = () => import('../views/Community.vue')
const SupportCause = () => import('../views/SupportCause.vue')
const NotFoundPage = () => import('../views/NotFoundPage.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: HomePage,
    meta: { requiresAuth: false },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { requiresAuth: false },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresAuth: false },
  },
  {
    path: '/terms',
    name: 'TermsOfService',
    component: TermsOfService,
    meta: { requiresAuth: false },
  },
  {
    path: '/privacy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicy,
    meta: { requiresAuth: false },
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true },
  },
  {
    path: '/tracks',
    name: 'AvailableTracks',
    component: AvailableTracks,
    meta: { requiresAuth: true },
  },
  {
    path: '/track/:trackId',
    name: 'TrackDetail',
    component: TrackDetail,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/track/:trackId/lesson/:lessonId',
    name: 'LessonView',
    component: LessonView,
    meta: { requiresAuth: true },
    props: true,
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfilePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/certificates',
    name: 'Certificates',
    component: CertificatePage,
    meta: { requiresAuth: true },
  },
  {
    path: '/community',
    name: 'Community',
    component: Community,
    meta: { requiresAuth: true },
  },
  {
    path: '/support',
    name: 'SupportCause',
    component: SupportCause,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin',
    name: 'AdminPanel',
    component: AdminPanel,
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFoundPage,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation guard - Check authentication
router.beforeEach((to) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    return { name: 'Login', query: { redirect: to.fullPath } }
  }

  if (to.meta.requiresAdmin && !(userStore.user as { is_staff?: boolean } | null)?.is_staff) {
    return { name: 'Home' }
  }

  if ((to.name === 'Login' || to.name === 'Register') && userStore.isAuthenticated) {
    return { name: 'Dashboard' }
  }

  return true
})

export default router
