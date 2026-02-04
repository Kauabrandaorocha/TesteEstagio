<template>
  <nav class="main-nav">
    <router-link to="/">Início</router-link>
  </nav>
  
  <router-view />
</template>

<style>
/* Estilos globais simples */
body { font-family: sans-serif; background-color: #f4f7f6; margin: 0; color: #333; }
.main-nav { background: #2c3e50; padding: 1rem; margin-bottom: 2rem; }
.main-nav a { color: white; text-decoration: none; font-weight: bold; }
</style>