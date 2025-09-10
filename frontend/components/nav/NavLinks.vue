<script setup lang="ts">
import { navigationLinks } from "~/data/links";
</script>

<template>
    <a
        v-for="link in navigationLinks"
        :key="link.href"
        :href="link.href"
        class="text-gray-700 hover:text-indigo-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200">
        {{ link.label }}
    </a>
</template>
