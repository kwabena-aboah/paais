<template>
  <div class="not-found-page">
    <div class="container">
      <div class="not-found-content">
        <div class="error-code">404</div>
        <h1>Page Not Found</h1>
        <p>Sorry, the page you're looking for doesn't exist or has been moved.</p>

        <div class="action-buttons">
          <router-link to="/" class="btn btn-primary btn-lg">
            <i class="fas fa-home"></i> Go Home
          </router-link>
          <router-link
            v-if="route.query.from !== '/'"
            to="/dashboard"
            class="btn btn-outline-primary btn-lg"
          >
            <i class="fas fa-arrow-left"></i> Go Back
          </router-link>
        </div>

        <div class="suggestions">
          <h4>Popular Pages:</h4>
          <ul>
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/dashboard">Dashboard</router-link></li>
            <li><router-link to="/login">Login</router-link></li>
            <li><router-link to="/register">Register</router-link></li>
          </ul>
        </div>
      </div>

      <div class="error-illustration">
        <svg viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg">
          <!-- 404 illustration -->
          <circle cx="100" cy="100" r="90" fill="var(--lav)" opacity="0.5" />
          <text
            x="100"
            y="120"
            font-size="60"
            font-weight="bold"
            text-anchor="middle"
            fill="var(--secondary-color)"
          >
            ?
          </text>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()
</script>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-deep) 100%);
  padding: 2rem;
  margin-top: 0px;
}

.container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4rem;
  align-items: center;
  max-width: 1000px;
}

.not-found-content {
  color: white;
}

.error-code {
  font-family: var(--font-poppins);
  font-size: 6rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--cyan) 0%, var(--magenta) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 1rem;
}

.not-found-content h1 {
  font-family: var(--font-poppins);
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: white;
}

.not-found-content p {
  font-size: 1.1rem;
  opacity: 0.9;
  margin-bottom: 2rem;
}

.action-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 3rem;
  flex-wrap: wrap;
}

.btn {
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-weight: 600;
}

.btn-primary {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
  color: white;
}

.btn-primary:hover {
  background-color: #d400e6;
  border-color: #d400e6;
}

.btn-outline-primary {
  border-color: white;
  color: white;
}

.btn-outline-primary:hover {
  background-color: white;
  color: var(--navy);
}

.suggestions {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 1.5rem;
}

.suggestions h4 {
  color: var(--cyan);
  margin-bottom: 1rem;
}

.suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.suggestions li {
  margin-bottom: 0.5rem;
}

.suggestions a {
  color: white;
  text-decoration: none;
  transition: all 0.2s ease;
}

.suggestions a:hover {
  color: var(--cyan);
  text-decoration: underline;
}

.error-illustration {
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-illustration svg {
  width: 100%;
  max-width: 300px;
  filter: drop-shadow(0 0 20px rgba(46, 230, 214, 0.3));
}

@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
    gap: 2rem;
  }

  .error-code {
    font-size: 4rem;
  }

  .not-found-content h1 {
    font-size: 2rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }

  .suggestions ul {
    grid-template-columns: 1fr;
  }
}
</style>
