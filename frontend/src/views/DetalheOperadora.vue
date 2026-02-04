<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { operadorasService } from '../services/api';
import type { Operadora, Despesa, PaginatedResponse } from '../types';
// Importando o componente que criamos
import HistoryChart from '../components/HistoryChart.vue';

const route = useRoute();
const cnpj = route.params.cnpj as string;

// Estados reativos com tipagem
const operadora = ref<Operadora | null>(null);
const despesas = ref<Despesa[]>([]);
const loading = ref(true);
const error = ref<string | null>(null);

const estatisticas = ref<any>(null);

const carregarDados = async () => {
  try {
    loading.value = true;
    error.value = null;

    const cnpjLimpo = cnpj.replace(/\D/g, ''); 

    const [resDet, resDesp] = await Promise.all([
      operadorasService.getDetalhe(cnpjLimpo),
      operadorasService.getDespesas(cnpjLimpo, 1)
    ]);

    // Cadastro
    operadora.value = resDet.data;
    
    // Despesas e Estatísticas
    if (resDesp && resDesp.data) {
      const corpo = resDesp.data;
      
      // Se o seu Python retornar {"data": [...], "estatisticas": {...}}
      despesas.value = corpo.data || [];
      estatisticas.value = corpo.estatisticas || null;
      
      console.log("Dados Financeiros:", corpo);
    }

  } catch (err: any) {
    console.error("Erro capturado no Catch:", err);
    error.value = "Erro ao carregar os dados. Verifique a conexão.";
  } finally {
    loading.value = false;
  }
};

onMounted(carregarDados);

// Utilitário para formatar valores monetários
const formatarMoeda = (valor: number) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor);
};

</script>

<template>
  <div class="detalhe-container">
    <router-link to="/" class="btn-voltar">← Voltar para a Lista</router-link>

    <div v-if="loading" class="state-msg">Carregando dados da operadora...</div>
    <div v-else-if="error" class="state-msg error">{{ error }}</div>

    <div v-else-if="operadora">
      <header class="main-header">
        <h1>{{ operadora.razao_social }}</h1>
        <div class="badges">
          <span><strong>CNPJ:</strong> {{ operadora.cnpj }}</span>
          <span><strong>Registro ANS:</strong> {{ operadora.registro_operadora }}</span>
        </div>
      </header>

      <div class="content-grid">
        <aside class="info-sidebar">
          <div class="card">
            <h3>Informações de Contato</h3>
            <p><strong>Cidade/UF:</strong> {{ operadora.cidade }} / {{ operadora.uf }}</p>
            <p><strong>E-mail:</strong> {{ operadora.endereco_eletronico || 'Não informado' }}</p>
            <p><strong>Representante:</strong> {{ operadora.representante }}</p>
            <p><strong>Modalidade:</strong> {{ operadora.modalidade }}</p>
          </div>
        </aside>

        <main class="chart-section">
          <div class="card">
            <h3>Evolução Financeira (Despesas)</h3>
            <HistoryChart v-if="despesas.length" :historico="despesas" />
            <div v-else class="no-data">Nenhum histórico de despesas encontrado.</div>
          </div>
        </main>
      </div>

      <section class="history-table">
        <div class="card">
          <h3>Histórico Trimestral Detalhado</h3>
          <table v-if="despesas.length">
            <thead>
              <tr>
                <th>Ano</th>
                <th>Trimestre</th>
                <th>Valor da Despesa</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(d, idx) in despesas" :key="idx">
                <td>{{ d.ano }}</td>
                <td>{{ d.trimestre }}º Trimestre</td>
                <td class="valor">{{ formatarMoeda(d.valor_despesas || 0) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.detalhe-container { padding: 20px; max-width: 1200px; margin: 0 auto; }
.btn-voltar { color: #42b983; text-decoration: none; font-weight: bold; display: inline-block; margin-bottom: 20px; }

.main-header { margin-bottom: 30px; }
.badges { display: flex; gap: 20px; color: #666; font-size: 0.9rem; }

.content-grid { display: grid; grid-template-columns: 350px 1fr; gap: 20px; margin-bottom: 20px; }
.card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); height: 100%; }
.card h3 { margin-top: 0; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }

.history-table { margin-top: 20px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 12px; text-align: left; border-bottom: 1px solid #eee; }
.valor { font-weight: bold; color: #2c3e50; }

.state-msg { text-align: center; padding: 50px; font-size: 1.2rem; }
.error { color: #e74c3c; }
.no-data { padding: 40px; text-align: center; color: #999; }

@media (max-width: 900px) {
  .content-grid { grid-template-columns: 1fr; }
}
</style>