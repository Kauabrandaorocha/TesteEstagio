<script setup lang="ts">
import type { Operadora } from '../types';

defineProps<{
  items: Operadora[]
}>();
</script>

<template>
  <table class="custom-table">
    <thead>
      <tr>
        <th>CNPJ</th>
        <th>Razão Social</th>
        <th>UF</th>
        <th>Ações</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="op in items" :key="op.cnpj">
        <td>{{ op.cnpj }}</td>
        <td>{{ op.razao_social }}</td>
        <td><span class="uf-badge">{{ op.uf }}</span></td>
        <td>
          <router-link :to="{ name: 'Detalhe', params: { cnpj: op.cnpj } }" class="btn-link">
            Detalhes
          </router-link>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<style scoped>
.custom-table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid #eee; }
th { background-color: #f8f9fa; }
.uf-badge { background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-weight: bold; }
.btn-link { color: #42b983; text-decoration: none; font-weight: bold; }
</style>