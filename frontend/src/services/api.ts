import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

const api = axios.create({
  baseURL: `${API_URL}/api`,
});

export const operadorasService = {
  getOperadoras(page: number, limit: number, search?: string) {
    return api.get('/operadoras', {
      params: { page, limit, search }
    });
  },
  getDetalhe(cnpj: string) {
    return api.get(`/operadoras/${cnpj}`);
  },
  getDespesas(cnpj: string, page: number = 1) {
    return api.get(`/operadoras/${cnpj}/despesas`, {
      params: { page, limit: 12 }
    });
  },
  getEstatisticas() {
    return api.get('/estatisticas');
  }
};