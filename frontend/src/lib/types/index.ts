// Type definitions matching backend Pydantic schemas

export interface Company {
  id: number;
  name: string;
  ir_url: string;
  primary_ticker: string | null;
  tickers: Array<{ [key: string]: string }> | null;
  created_at: string | null;
}

export interface CompanyCreate {
  name: string;
  ir_url: string;
  primary_ticker?: string | null;
  tickers?: Array<{ [key: string]: string }> | null;
}

export interface Document {
  id: number;
  company_id: number;
  url: string;
  fiscal_year: number;
  document_type: string;
  file_path: string | null;
  created_at: string | null;
}

export interface CompiledStatement {
  id: number;
  company_id: number;
  statement_type: string;
  data: Record<string, any>; // Financial data structure
  updated_at: string | null;
}

export interface TaskResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface TaskStatus {
  task_id: string;
  status: "PENDING" | "STARTED" | "SUCCESS" | "FAILURE" | "RETRY" | "REVOKED";
  result: Record<string, any> | null;
  error: string | null;
}

export type StatementType = "income_statement" | "balance_sheet" | "cash_flow_statement";

export interface StoragePdfFile {
  object_key: string;
  size: number;
  last_modified: string | null;
  content_type: string;
}

export interface StoragePdfListResponse {
  company_id: number;
  fiscal_year: number | null;
  prefix: string;
  count: number;
  files: StoragePdfFile[];
}
