export interface Parameter { name: string; label: string; kind: 'int'|'float'|'date'|'string'; default: string|number }
export interface Exercise { code: string; group: string; title: string; description: string; sql: string; params: Parameter[] }
export interface Topic { id: string; title: string; target: number }
export interface Catalog { groups: Topic[]; exercises: Exercise[]; total: number }
export interface DbState { connected: boolean; ready: boolean; database?: string; message: string }
export interface RunResult { code: string; title: string; columns: string[]; rows: Record<string, unknown>[]; truncated?: boolean; duration_ms: number; message: string }
