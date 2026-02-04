<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { operadorasService } from '../services/api';
import { Bar } from 'vue-chartjs';
import { 
  Chart as ChartJS, 
  Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale 
} from 'chart.js';

// Registrar os módulos do Chart.js
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const chartData = ref<any>(null);
const loading = ref(true);

// --- AQUI FICA O OPTIONS ---
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }, // Oculta a legenda para ficar mais limpo
    tooltip: {
      callbacks: {
        // Formata o valor para Real Brasileiro ao passar o mouse
        label: (context: any) => {
          return new Intl.NumberFormat('pt-BR', { 
            style: 'currency', 
            currency: 'BRL' 
          }).format(context.raw);
        }
      }
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        // Formata os números do eixo Y
        callback: (value: any) => {
          return new Intl.NumberFormat('pt-BR', { 
            notation: 'compact', 
            compactDisplay: 'short' 
          }).format(value);
        }
      }
    }
  }
};

onMounted(async () => {
  try {
    const res = await operadorasService.getEstatisticas();
    const dados = res.data.despesas_por_uf;

    chartData.value = {
      labels: dados.map((d: any) => d.uf),
      datasets: [{
        label: 'Despesas por UF',
        backgroundColor: '#3498db',
        borderRadius: 5,
        data: dados.map((d: any) => d.total)
      }]
    };
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="stats-card">
    <h3>Distribuição de Despesas por Estado (UF)</h3>
    <div v-if="loading" class="placeholder">Carregando estatísticas...</div>
    <div v-else-if="chartData" class="chart-container">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.stats-card { background: white; padding: 20px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
.chart-container { height: 350px; }
.placeholder { height: 350px; display: flex; align-items: center; justify-content: center; color: #666; }
</style>