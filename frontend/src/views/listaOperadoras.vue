<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useOperadoras } from '../composables/useOperadoras';
import StatsDashboard from '../components/StatsDashboard.vue';
import OperadoraTable from '../components/OperadoraTable.vue'; // Vamos criar este abaixo

const { operadoras, loading, meta, listar } = useOperadoras();

const searchTerm = ref('');
const currentPage = ref(1);

// Lógica de busca com Debounce
let timeout: ReturnType<typeof setTimeout>;
watch(searchTerm, () => {
  clearTimeout(timeout);
  timeout = setTimeout(() => {
    currentPage.value = 1;
    listar(currentPage.value, searchTerm.value);
  }, 500);
});

const mudarPagina = (novaPagina: number) => {
  currentPage.value = novaPagina;
  listar(currentPage.value, searchTerm.value);
};

onMounted(() => {
  listar(currentPage.value);
});
</script>

<template>
  <div class="container">
    <StatsDashboard />

    <div class="search-section">
      <h2>Listagem de Operadoras</h2>
      <input 
        v-model="searchTerm" 
        type="text" 
        placeholder="Filtrar por Razão Social ou CNPJ..." 
        class="search-input"
      />
    </div>

    <div v-if="loading" class="loading-state">Carregando dados...</div>
    
    <div v-else>
      <OperadoraTable :items="operadoras" />

      <div class="pagination" v-if="meta && meta.total_pages > 1">
        <button :disabled="currentPage === 1" @click="mudarPagina(currentPage - 1)">Anterior</button>
        <span>Página {{ currentPage }} de {{ meta.total_pages }}</span>
        <button :disabled="currentPage === meta.total_pages" @click="mudarPagina(currentPage + 1)">Próxima</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.search-section { margin: 20px 0; }
.search-input { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; font-size: 1rem; }
.pagination { display: flex; justify-content: center; align-items: center; gap: 20px; margin-top: 20px; }
.loading-state { text-align: center; padding: 40px; }
</style>