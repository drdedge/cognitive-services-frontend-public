<template>
  <div id="app" class="min-h-screen bg-background">
    <!-- Navigation Header -->
    <nav class="bg-header-bg shadow-lg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <!-- Logo/Title -->
            <router-link to="/" class="flex items-center space-x-3">
              <!-- Logo SVG -->
              <svg class="h-8 w-8 text-white" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Brain/AI Icon -->
                <path d="M12 2C10.9 2 10 2.9 10 4C10 4.33 10.08 4.64 10.21 4.91C9.49 5.27 9 6.04 9 6.92C9 7.55 9.26 8.11 9.66 8.52C9.26 8.94 9 9.5 9 10.13C9 11.16 9.84 12 10.88 12H11V16.41C10.41 16.74 10 17.36 10 18.08C10 19.14 10.86 20 11.92 20C12.64 20 13.26 19.59 13.59 19H14.41C14.74 19.59 15.36 20 16.08 20C17.14 20 18 19.14 18 18.08C18 17.36 17.59 16.74 17 16.41V12H17.12C18.16 12 19 11.16 19 10.13C19 9.5 18.74 8.94 18.34 8.52C18.74 8.11 19 7.55 19 6.92C19 6.04 18.51 5.27 17.79 4.91C17.92 4.64 18 4.33 18 4C18 2.9 17.1 2 16 2H12Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="12" cy="9" r="2" fill="currentColor" opacity="0.3"/>
                <circle cx="8" cy="14" r="1.5" fill="currentColor" opacity="0.3"/>
                <circle cx="16" cy="14" r="1.5" fill="currentColor" opacity="0.3"/>
              </svg>
              <h1 class="text-xl font-semibold text-white">
                Azure Cognitive Services
              </h1>
            </router-link>

            <!-- Navigation Links -->
            <div class="hidden sm:ml-8 sm:flex sm:space-x-8">
              <router-link
                v-for="item in navigation"
                :key="item.name"
                :to="item.to"
                class="nav-link"
                :class="{ 'nav-link-active': $route.path === item.to }"
              >
                {{ item.name }}
              </router-link>
            </div>
          </div>

          <!-- Mobile menu button -->
          <div class="flex items-center sm:hidden">
            <button
              @click="mobileMenuOpen = !mobileMenuOpen"
              class="inline-flex items-center justify-center p-2 rounded-md text-gray-300 hover:text-white hover:bg-primary-action"
            >
              <svg
                class="h-6 w-6"
                :class="{ 'hidden': mobileMenuOpen, 'block': !mobileMenuOpen }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg
                class="h-6 w-6"
                :class="{ 'block': mobileMenuOpen, 'hidden': !mobileMenuOpen }"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Mobile menu -->
      <div v-if="mobileMenuOpen" class="sm:hidden bg-header-bg">
        <div class="pt-2 pb-3 space-y-1">
          <router-link
            v-for="item in navigation"
            :key="item.name"
            :to="item.to"
            class="mobile-nav-link"
            :class="{ 'mobile-nav-link-active': $route.path === item.to }"
            @click="mobileMenuOpen = false"
          >
            {{ item.name }}
          </router-link>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-auto">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex flex-col sm:flex-row justify-between items-center space-y-2 sm:space-y-0">
          <p class="text-sm text-gray-600">
            Powered by Azure Cognitive Services
          </p>
          <div class="flex items-center space-x-2 text-sm">
            <span class="text-gray-600">Built by</span>
            <a 
              href="https://github.com/drdedge" 
              target="_blank" 
              rel="noopener noreferrer"
              class="text-primary-action hover:text-highlight transition-colors duration-200 font-semibold"
            >
              drdedge
            </a>
            <span class="text-gray-400">•</span>
            <span class="text-gray-600">Open-sourced for enterprises</span>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const mobileMenuOpen = ref(false)

const navigation = [
  { name: 'Home', to: '/' },
  { name: 'Usage', to: '/usage' },
  { name: 'Document Intelligence', to: '/document-intelligence' },
  { name: 'Translation', to: '/translation' },
  { name: 'Transcription', to: '/transcription' },
]
</script>

<style scoped>
.nav-link {
  @apply inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-300 hover:text-white hover:border-highlight transition-colors duration-200;
}

.nav-link-active {
  @apply border-highlight text-white;
}

.mobile-nav-link {
  @apply block pl-3 pr-4 py-2 border-l-4 border-transparent text-base font-medium text-gray-300 hover:text-white hover:bg-primary-action hover:border-highlight;
}

.mobile-nav-link-active {
  @apply bg-primary-action border-highlight text-white;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>