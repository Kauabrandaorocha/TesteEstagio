export interface Operadora {
  cnpj: string;
  razao_social: string;
  uf: string;
  registro_operadora?: string;
  nome_fantasia?: string;
  modalidade?: string;
  logradouro?: string;
  numero?: string;
  bairro?: string;
  cidade?: string;
  endereco_eletronico?: string;
  representante?: string;
}

export interface Despesa {
  ano: number;
  trimestre: number;
  valor_despesas: number;
}

export interface EstatisticaUF {
  uf: string;
  total: number;
}

export interface Meta {
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}

export interface PaginatedResponse<T> {
  data: T[];
  meta: Meta;
  cnpj?: string; // Usado na resposta de despesas
}

export interface StatsResponse {
  total_despesas: number;
  media_despesas: number;
  despesas_por_uf: EstatisticaUF[];
  top_5_operadoras: Array<{ razao_social: string; total_despesas: number }>;
}