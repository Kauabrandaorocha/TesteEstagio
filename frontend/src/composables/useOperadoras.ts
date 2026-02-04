import { ref } from 'vue';
import { operadorasService } from '../services/api';
import type { Operadora, Meta, PaginatedResponse } from '../types';

export function useOperadoras() {
  const operadoras = ref<Operadora[]>([]);
  const meta = ref<Meta | null>(null);
  const loading = ref(false);

  const listar = async (page: number, search?: string) => {
    loading.value = true;
    try {
      console.log("Iniciando busca com:", { page, search }); // <--- LOG 1
      
      const response = await operadorasService.getOperadoras(page, 10, search);
      
      console.log("Resposta do Back:", response.data); // <--- LOG 2

      // Verifique se a estrutura bate com o que estamos atribuindo
      const resData = response.data as PaginatedResponse<Operadora>;
      operadoras.value = resData.data;
      meta.value = resData.meta;
      
    } catch (err) {
      console.error("Erro na busca:", err); // <--- LOG DE ERRO
    } finally {
      loading.value = false;
    }
  };

  return { operadoras, meta, loading, listar };
}