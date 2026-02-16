import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import * as api from "../lib/api";
import type { GarmentCreateRequest, GarmentTransitionRequest, AddMaterialRequest, AddAttributeRequest, AssociateSupplierRequest, SupplierTransitionRequest } from "../types";

export function useGarments(stage?: string) {
  return useQuery({
    queryKey: ["garments", { stage }],
    queryFn: () => api.getGarments(stage),
  });
}

export function useGarment(id: number) {
  return useQuery({
    queryKey: ["garments", id],
    queryFn: () => api.getGarment(id),
  });
}

export function useCreateGarment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: GarmentCreateRequest) => api.createGarment(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["garments"] }),
  });
}

export function useDeleteGarment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteGarment(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["garments"] }),
  });
}

export function useTransitionGarment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: GarmentTransitionRequest }) =>
      api.transitionGarment(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["garments"] }),
  });
}

export function useCreateVariation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ parentId, data }: { parentId: number; data: GarmentCreateRequest }) =>
      api.createVariation(parentId, data),
    onSuccess: (_, { parentId }) => {
      qc.invalidateQueries({ queryKey: ["garments"] });
      qc.invalidateQueries({ queryKey: ["garments", parentId] });
    },
  });
}

export function useAddMaterial() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ garmentId, data }: { garmentId: number; data: AddMaterialRequest }) =>
      api.addMaterial(garmentId, data),
    onSuccess: (_, { garmentId }) =>
      qc.invalidateQueries({ queryKey: ["garments", garmentId] }),
  });
}

export function useRemoveMaterial() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ garmentId, materialId }: { garmentId: number; materialId: number }) =>
      api.removeMaterial(garmentId, materialId),
    onSuccess: (_, { garmentId }) =>
      qc.invalidateQueries({ queryKey: ["garments", garmentId] }),
  });
}

export function useAddAttribute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ garmentId, data }: { garmentId: number; data: AddAttributeRequest }) =>
      api.addAttribute(garmentId, data),
    onSuccess: (_, { garmentId }) =>
      qc.invalidateQueries({ queryKey: ["garments", garmentId] }),
  });
}

export function useRemoveAttribute() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ garmentId, attributeId }: { garmentId: number; attributeId: number }) =>
      api.removeAttribute(garmentId, attributeId),
    onSuccess: (_, { garmentId }) =>
      qc.invalidateQueries({ queryKey: ["garments", garmentId] }),
  });
}

export function useAssociateSupplier() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ garmentId, data }: { garmentId: number; data: AssociateSupplierRequest }) =>
      api.associateSupplier(garmentId, data),
    onSuccess: (_, { garmentId }) =>
      qc.invalidateQueries({ queryKey: ["garments", garmentId] }),
  });
}

export function useTransitionSupplier() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ garmentId, supplierId, data }: { garmentId: number; supplierId: number; data: SupplierTransitionRequest }) =>
      api.transitionSupplier(garmentId, supplierId, data),
    onSuccess: (_, { garmentId }) =>
      qc.invalidateQueries({ queryKey: ["garments", garmentId] }),
  });
}
