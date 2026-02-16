import type {
  Garment, GarmentDetail, GarmentCreateRequest, GarmentUpdateRequest,
  GarmentTransitionRequest, AddMaterialRequest, AddAttributeRequest,
  AssociateSupplierRequest, SupplierTransitionRequest, GarmentSupplierDetail,
  Material, Attribute, Supplier, SampleSet,
} from "../types";

const API_BASE = "/api";

class ApiError extends Error {
  code: string;
  constructor(code: string, detail: string) {
    super(detail);
    this.code = code;
  }
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({ error: "UNKNOWN", detail: "An error occurred" }));
    throw new ApiError(body.error || "UNKNOWN", body.detail || "An error occurred");
  }

  if (response.status === 204) return null as T;
  return response.json();
}

// Garments
export const getGarments = (stage?: string, search?: string): Promise<Garment[]> => {
  const params = new URLSearchParams();
  if (stage) params.set("stage", stage);
  if (search) params.set("search", search);
  const qs = params.toString();
  return request(`/garments${qs ? `?${qs}` : ""}`);
};

export const getGarment = (id: number): Promise<GarmentDetail> =>
  request(`/garments/${id}`);

export const createGarment = (data: GarmentCreateRequest): Promise<Garment> =>
  request("/garments", { method: "POST", body: JSON.stringify(data) });

export const updateGarment = (id: number, data: GarmentUpdateRequest): Promise<Garment> =>
  request(`/garments/${id}`, { method: "PUT", body: JSON.stringify(data) });

export const deleteGarment = (id: number): Promise<void> =>
  request(`/garments/${id}`, { method: "DELETE" });

export const transitionGarment = (id: number, data: GarmentTransitionRequest): Promise<Garment> =>
  request(`/garments/${id}/transition`, { method: "POST", body: JSON.stringify(data) });

export const createVariation = (parentId: number, data: GarmentCreateRequest): Promise<Garment> =>
  request(`/garments/${parentId}/variations`, { method: "POST", body: JSON.stringify(data) });

// Garment Materials
export const addMaterial = (garmentId: number, data: AddMaterialRequest): Promise<void> =>
  request(`/garments/${garmentId}/materials`, { method: "POST", body: JSON.stringify(data) });

export const removeMaterial = (garmentId: number, materialId: number): Promise<void> =>
  request(`/garments/${garmentId}/materials/${materialId}`, { method: "DELETE" });

// Garment Attributes
export const addAttribute = (garmentId: number, data: AddAttributeRequest): Promise<void> =>
  request(`/garments/${garmentId}/attributes`, { method: "POST", body: JSON.stringify(data) });

export const removeAttribute = (garmentId: number, attributeId: number): Promise<void> =>
  request(`/garments/${garmentId}/attributes/${attributeId}`, { method: "DELETE" });

// Garment Suppliers
export const associateSupplier = (garmentId: number, data: AssociateSupplierRequest): Promise<GarmentSupplierDetail> =>
  request(`/garments/${garmentId}/suppliers`, { method: "POST", body: JSON.stringify(data) });

export const transitionSupplier = (garmentId: number, supplierId: number, data: SupplierTransitionRequest): Promise<GarmentSupplierDetail> =>
  request(`/garments/${garmentId}/suppliers/${supplierId}/transition`, { method: "POST", body: JSON.stringify(data) });

// Sample Sets
export const getSampleSets = (garmentId: number, supplierId: number): Promise<SampleSet[]> =>
  request(`/garments/${garmentId}/suppliers/${supplierId}/samples`);

export const createSampleSet = (garmentId: number, supplierId: number, data: { notes?: string }): Promise<SampleSet> =>
  request(`/garments/${garmentId}/suppliers/${supplierId}/samples`, { method: "POST", body: JSON.stringify(data) });

// Materials (reference data)
export const getMaterials = (): Promise<Material[]> =>
  request("/materials");

// Attributes (reference data)
export const getAttributes = (category?: string): Promise<Attribute[]> => {
  const qs = category ? `?category=${category}` : "";
  return request(`/attributes${qs}`);
};

// Suppliers (reference data)
export const getSuppliers = (): Promise<Supplier[]> =>
  request("/suppliers");
