// Matches backend/app/schemas/garment.py
export interface Garment {
  id: number;
  name: string;
  description: string | null;
  lifecycle_stage: LifecycleStage;
  parent_garment_id: number | null;
  created_at: string;
  updated_at: string;
}

export type LifecycleStage = "CONCEPT" | "DESIGN" | "DEVELOPMENT" | "SAMPLING" | "PRODUCTION";

export interface GarmentMaterial {
  id: number;
  name: string;
  percentage: number;
}

export interface GarmentAttribute {
  id: number;
  name: string;
  category: string;
}

export interface GarmentSupplierSummary {
  supplier_id: number;
  supplier_name: string;
  status: string;
  offer_price: number | null;
}

export interface GarmentVariation {
  id: number;
  name: string;
  lifecycle_stage: string;
}

export interface GarmentDetail extends Garment {
  materials: GarmentMaterial[];
  attributes: GarmentAttribute[];
  suppliers: GarmentSupplierSummary[];
  variations: GarmentVariation[];
}

// Matches backend/app/schemas/material.py
export interface Material {
  id: number;
  name: string;
}

// Matches backend/app/schemas/attribute.py
export interface Attribute {
  id: number;
  name: string;
  category: string;
}

// Matches backend/app/schemas/supplier.py
export interface Supplier {
  id: number;
  name: string;
  contact_info: string | null;
  created_at: string;
}

export type SupplierStatus = "OFFERED" | "SAMPLING" | "APPROVED" | "REJECTED" | "IN_PRODUCTION" | "IN_STORE";

export interface GarmentSupplierDetail {
  id: number;
  garment_id: number;
  supplier_id: number;
  supplier_name: string | null;
  status: SupplierStatus;
  offer_price: number | null;
  lead_time_days: number | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// Matches backend/app/schemas/sample_set.py
export interface SampleSet {
  id: number;
  garment_supplier_id: number;
  status: string;
  notes: string | null;
  submitted_date: string | null;
  created_at: string;
  updated_at: string;
}

// Request types
export interface GarmentCreateRequest {
  name: string;
  description?: string;
}

export interface GarmentUpdateRequest {
  name?: string;
  description?: string;
}

export interface GarmentTransitionRequest {
  target_stage: string;
}

export interface AddMaterialRequest {
  material_id: number;
  percentage: number;
}

export interface AddAttributeRequest {
  attribute_id: number;
}

export interface AssociateSupplierRequest {
  supplier_id: number;
  offer_price?: number;
  lead_time_days?: number;
  notes?: string;
}

export interface SupplierTransitionRequest {
  target_status: string;
}

// Error response from backend
export interface ApiError {
  error: string;
  detail: string;
}

// Lifecycle constants (mirrors backend/app/services/lifecycle.py)
export const LIFECYCLE_STAGES: LifecycleStage[] = [
  "CONCEPT", "DESIGN", "DEVELOPMENT", "SAMPLING", "PRODUCTION"
];

export const GARMENT_TRANSITIONS: Record<string, string[]> = {
  CONCEPT: ["DESIGN"],
  DESIGN: ["CONCEPT", "DEVELOPMENT"],
  DEVELOPMENT: ["DESIGN", "SAMPLING"],
  SAMPLING: ["DEVELOPMENT", "PRODUCTION"],
  PRODUCTION: [],
};

export const SUPPLIER_TRANSITIONS: Record<string, string[]> = {
  OFFERED: ["SAMPLING", "REJECTED"],
  SAMPLING: ["APPROVED", "REJECTED"],
  APPROVED: ["IN_PRODUCTION", "REJECTED"],
  REJECTED: [],
  IN_PRODUCTION: ["IN_STORE"],
  IN_STORE: [],
};
