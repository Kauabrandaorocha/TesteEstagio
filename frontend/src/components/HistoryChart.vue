<script setup lang="ts">
import { computed } from 'vue';
import { Line } from 'vue-chartjs';
import type { Despesa } from '../types';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  CategoryScale,
  Filler,
  type ChartData
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, LineElement, LinearScale, PointElement, CategoryScale, Filler);

// Definindo as props que o componente recebe
const props = defineProps<{
  historico: Despesa[]
}>();

const chartData = computed<ChartData<'line'>>(() => {
  // 1. Filtra apenas o que for objeto válido e tiver ano/trimestre (evita a frase de erro do backend)
  const dadosValidos = props.historico.filter(d => typeof d === 'object' && d.ano);

  // 2. Ordena
  const ordenado = [...dadosValidos].sort((a, b) => a.ano - b.ano || a.trimestre - b.trimestre);

  return {
    labels: ordenado.map(d => `${d.trimestre}º Trim / ${d.ano}`),
    datasets: [
      {
        label: 'Despesas Trimestrais',
        borderColor: '#42b983',
        backgroundColor: 'rgba(66, 185, 131, 0.2)',
        // 3. Garante que o valor seja número para não dar NaN
        data: ordenado.map(d => Number(d.valor_despesas) || 0),
        fill: true,
        tension: 0.4
      }
    ]
  };
});
</script>

<template>
  <div class="chart-wrapper">
    <Line :data="chartData" :options="{ responsive: true, maintainAspectRatio: false }" />
  </div>
</template>

<style scoped>
.chart-wrapper { height: 350px; width: 100%; }
</style>