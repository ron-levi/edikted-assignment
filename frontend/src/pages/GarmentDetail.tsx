import { useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import { useGarment, useTransitionGarment, useAddMaterial, useRemoveMaterial, useAddAttribute, useRemoveAttribute, useAssociateSupplier, useTransitionSupplier, useCreateVariation, useDeleteGarment } from "../hooks/useGarments";
import { useMaterials } from "../hooks/useMaterials";
import { useAttributes } from "../hooks/useAttributes";
import { useSuppliers } from "../hooks/useSuppliers";
import { LIFECYCLE_STAGES, GARMENT_TRANSITIONS, SUPPLIER_TRANSITIONS } from "../types";
import type { LifecycleStage } from "../types";
import { Badge } from "../components/ui/Badge";
import { Modal } from "../components/ui/Modal";
import { Spinner } from "../components/ui/Spinner";

export function GarmentDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const garmentId = Number(id);
  const { data: garment, isLoading, error } = useGarment(garmentId);

  const transitionMutation = useTransitionGarment();
  const addMaterialMutation = useAddMaterial();
  const removeMaterialMutation = useRemoveMaterial();
  const addAttributeMutation = useAddAttribute();
  const removeAttributeMutation = useRemoveAttribute();
  const associateSupplierMutation = useAssociateSupplier();
  const transitionSupplierMutation = useTransitionSupplier();
  const createVariationMutation = useCreateVariation();
  const deleteMutation = useDeleteGarment();

  const { data: allMaterials } = useMaterials();
  const { data: allAttributes } = useAttributes();
  const { data: allSuppliers } = useSuppliers();

  // Add material form state
  const [matId, setMatId] = useState("");
  const [matPct, setMatPct] = useState("");

  // Add attribute form state
  const [attrId, setAttrId] = useState("");

  // Associate supplier form state
  const [suppId, setSuppId] = useState("");
  const [suppPrice, setSuppPrice] = useState("");
  const [suppLead, setSuppLead] = useState("");

  // Variation modal
  const [showVariation, setShowVariation] = useState(false);
  const [varName, setVarName] = useState("");
  const [varDesc, setVarDesc] = useState("");

  if (isLoading) return <Spinner />;
  if (error) return <div className="text-red-600">Error: {(error as Error).message}</div>;
  if (!garment) return <div>Not found</div>;

  const currentStageIdx = LIFECYCLE_STAGES.indexOf(garment.lifecycle_stage as LifecycleStage);
  const validTransitions = GARMENT_TRANSITIONS[garment.lifecycle_stage] || [];

  const handleTransition = async (targetStage: string) => {
    try {
      await transitionMutation.mutateAsync({ id: garmentId, data: { target_stage: targetStage } });
      toast.success(`Transitioned to ${targetStage}`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const handleAddMaterial = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await addMaterialMutation.mutateAsync({
        garmentId,
        data: { material_id: Number(matId), percentage: Number(matPct) },
      });
      toast.success("Material added");
      setMatId("");
      setMatPct("");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const handleAddAttribute = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await addAttributeMutation.mutateAsync({
        garmentId,
        data: { attribute_id: Number(attrId) },
      });
      toast.success("Attribute added");
      setAttrId("");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const handleAssociateSupplier = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await associateSupplierMutation.mutateAsync({
        garmentId,
        data: {
          supplier_id: Number(suppId),
          offer_price: suppPrice ? Number(suppPrice) : undefined,
          lead_time_days: suppLead ? Number(suppLead) : undefined,
        },
      });
      toast.success("Supplier associated");
      setSuppId("");
      setSuppPrice("");
      setSuppLead("");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const handleSupplierTransition = async (supplierId: number, targetStatus: string) => {
    try {
      await transitionSupplierMutation.mutateAsync({ garmentId, supplierId, data: { target_status: targetStatus } });
      toast.success(`Supplier status: ${targetStatus}`);
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const handleCreateVariation = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    try {
      await createVariationMutation.mutateAsync({
        parentId: garmentId,
        data: { name: varName.trim(), description: varDesc.trim() || undefined },
      });
      toast.success("Variation created");
      setShowVariation(false);
      setVarName("");
      setVarDesc("");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const handleDelete = async () => {
    if (!confirm(`Delete "${garment.name}"?`)) return;
    try {
      await deleteMutation.mutateAsync(garmentId);
      toast.success("Garment deleted");
      navigate("/");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  // Filter out already-assigned materials/attributes/suppliers from dropdowns
  const totalPct = garment.materials.reduce((sum, m) => sum + m.percentage, 0);
  const assignedMaterialIds = new Set(garment.materials.map((m) => m.id));
  const availableMaterials = allMaterials?.filter((m) => !assignedMaterialIds.has(m.id)) || [];

  const assignedAttributeIds = new Set(garment.attributes.map((a) => a.id));
  const availableAttributes = allAttributes?.filter((a) => !assignedAttributeIds.has(a.id)) || [];

  const assignedSupplierIds = new Set(garment.suppliers.map((s) => s.supplier_id));
  const availableSuppliers = allSuppliers?.filter((s) => !assignedSupplierIds.has(s.id)) || [];

  return (
    <div>
      {/* Header */}
      <div className="mb-6">
        <Link to="/" className="text-sm text-indigo-600 hover:text-indigo-800 mb-2 inline-block">&larr; Back to Dashboard</Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{garment.name}</h1>
            {garment.description && <p className="text-gray-500 mt-1">{garment.description}</p>}
            {garment.parent_garment_id && (
              <p className="text-sm text-gray-400 mt-1">
                Variation of <Link to={`/garments/${garment.parent_garment_id}`} className="text-indigo-600 hover:underline">#{garment.parent_garment_id}</Link>
              </p>
            )}
          </div>
          <button
            onClick={handleDelete}
            disabled={garment.lifecycle_stage === "PRODUCTION"}
            title={garment.lifecycle_stage === "PRODUCTION" ? "Cannot delete garments in PRODUCTION stage" : "Delete garment"}
            className={`text-red-500 hover:text-red-700 text-sm ${garment.lifecycle_stage === "PRODUCTION" ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            Delete
          </button>
        </div>
      </div>

      {/* Lifecycle Stepper */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Lifecycle</h2>
        <div className="flex items-center gap-2 mb-4">
          {LIFECYCLE_STAGES.map((stage, idx) => (
            <div key={stage} className="flex items-center">
              {idx > 0 && <div className={`w-8 h-0.5 ${idx <= currentStageIdx ? "bg-indigo-600" : "bg-gray-200"}`} />}
              <div
                className={`px-3 py-1.5 rounded-full text-xs font-medium ${
                  stage === garment.lifecycle_stage
                    ? "bg-indigo-600 text-white"
                    : idx < currentStageIdx
                    ? "bg-indigo-100 text-indigo-700"
                    : "bg-gray-100 text-gray-400"
                }`}
              >
                {stage}
              </div>
            </div>
          ))}
        </div>
        {validTransitions.length > 0 && (
          <div className="flex gap-2">
            {validTransitions.map((target) => {
              const isForward = LIFECYCLE_STAGES.indexOf(target as LifecycleStage) > currentStageIdx;
              return (
                <button
                  key={target}
                  onClick={() => handleTransition(target)}
                  disabled={transitionMutation.isPending}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium ${
                    isForward
                      ? "bg-indigo-600 text-white hover:bg-indigo-700"
                      : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                  } disabled:opacity-50`}
                >
                  {isForward ? `Advance to ${target}` : `Send Back to ${target}`}
                </button>
              );
            })}
          </div>
        )}
        {garment.lifecycle_stage === "PRODUCTION" && (
          <p className="text-sm text-gray-500 italic">Production is the final stage.</p>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Materials Panel */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold mb-4">Materials</h2>
          {garment.materials.length > 0 ? (
            <table className="w-full text-sm mb-4">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2">Material</th>
                  <th className="pb-2">Percentage</th>
                  <th className="pb-2"></th>
                </tr>
              </thead>
              <tbody>
                {garment.materials.map((m) => (
                  <tr key={m.id} className="border-b last:border-0">
                    <td className="py-2">{m.name}</td>
                    <td className="py-2">{m.percentage}%</td>
                    <td className="py-2 text-right">
                      <button
                        onClick={() => removeMaterialMutation.mutate({ garmentId, materialId: m.id })}
                        className="text-red-400 hover:text-red-600 text-xs"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-400 text-sm mb-4">No materials assigned.</p>
          )}
          <p className="text-sm text-gray-500 mb-2">Current total: {totalPct}% ({(100 - totalPct).toFixed(1)}% available)</p>
          <form onSubmit={handleAddMaterial} className="flex gap-2 items-end">
            <select
              value={matId}
              onChange={(e) => setMatId(e.target.value)}
              className="border rounded-lg px-2 py-1.5 text-sm flex-1"
              required
            >
              <option value="">Select material...</option>
              {availableMaterials.map((m) => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
            <input
              type="number"
              value={matPct}
              onChange={(e) => setMatPct(e.target.value)}
              placeholder="%"
              min="0.01"
              max={100 - totalPct}
              step="0.01"
              className="border rounded-lg px-2 py-1.5 text-sm w-20"
              required
            />
            <button type="submit" disabled={addMaterialMutation.isPending} className="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
              Add
            </button>
          </form>
        </div>

        {/* Attributes Panel */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold mb-4">Attributes</h2>
          {garment.attributes.length > 0 ? (
            <div className="flex flex-wrap gap-2 mb-4">
              {garment.attributes.map((a) => (
                <span key={a.id} className="inline-flex items-center gap-1 bg-gray-100 rounded-full px-3 py-1 text-sm">
                  <span className="text-gray-500 text-xs">{a.category}:</span> {a.name}
                  <button
                    onClick={() => removeAttributeMutation.mutate({ garmentId, attributeId: a.id })}
                    className="text-gray-400 hover:text-red-500 ml-1"
                  >
                    &times;
                  </button>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm mb-4">No attributes assigned.</p>
          )}
          <form onSubmit={handleAddAttribute} className="flex gap-2">
            <select
              value={attrId}
              onChange={(e) => setAttrId(e.target.value)}
              className="border rounded-lg px-2 py-1.5 text-sm flex-1"
              required
            >
              <option value="">Select attribute...</option>
              {availableAttributes.map((a) => (
                <option key={a.id} value={a.id}>[{a.category}] {a.name}</option>
              ))}
            </select>
            <button type="submit" disabled={addAttributeMutation.isPending} className="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
              Add
            </button>
          </form>
        </div>

        {/* Suppliers Panel */}
        <div className="bg-white rounded-lg shadow-sm border p-6 lg:col-span-2">
          <h2 className="text-lg font-semibold mb-4">Suppliers</h2>
          {garment.suppliers.length > 0 ? (
            <table className="w-full text-sm mb-4">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2">Supplier</th>
                  <th className="pb-2">Status</th>
                  <th className="pb-2">Price</th>
                  <th className="pb-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {garment.suppliers.map((s) => {
                  const transitions = SUPPLIER_TRANSITIONS[s.status] || [];
                  return (
                    <tr key={s.supplier_id} className="border-b last:border-0">
                      <td className="py-2">{s.supplier_name}</td>
                      <td className="py-2"><Badge label={s.status} /></td>
                      <td className="py-2">{s.offer_price != null ? `$${s.offer_price.toFixed(2)}` : "-"}</td>
                      <td className="py-2">
                        <div className="flex gap-1 flex-wrap">
                          {transitions.map((target) => {
                            const colorClass =
                              target === "REJECTED"
                                ? "bg-red-600 text-white hover:bg-red-700"
                                : target === "APPROVED" || target === "IN_PRODUCTION" || target === "IN_STORE"
                                ? "bg-green-600 text-white hover:bg-green-700"
                                : "bg-indigo-100 text-indigo-700 hover:bg-indigo-200";
                            return (
                              <button
                                key={target}
                                onClick={() => handleSupplierTransition(s.supplier_id, target)}
                                disabled={transitionSupplierMutation.isPending}
                                className={`px-2 py-0.5 rounded text-xs font-medium ${colorClass} disabled:opacity-50`}
                              >
                                {target.replace(/_/g, " ")}
                              </button>
                            );
                          })}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <p className="text-gray-400 text-sm mb-4">No suppliers associated.</p>
          )}
          <form onSubmit={handleAssociateSupplier} className="flex gap-2 items-end flex-wrap">
            <select
              value={suppId}
              onChange={(e) => setSuppId(e.target.value)}
              className="border rounded-lg px-2 py-1.5 text-sm"
              required
            >
              <option value="">Select supplier...</option>
              {availableSuppliers.map((s) => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
            <input
              type="number"
              value={suppPrice}
              onChange={(e) => setSuppPrice(e.target.value)}
              placeholder="Price"
              min="0"
              step="0.01"
              className="border rounded-lg px-2 py-1.5 text-sm w-24"
            />
            <input
              type="number"
              value={suppLead}
              onChange={(e) => setSuppLead(e.target.value)}
              placeholder="Lead days"
              min="1"
              className="border rounded-lg px-2 py-1.5 text-sm w-24"
            />
            <button type="submit" disabled={associateSupplierMutation.isPending} className="bg-indigo-600 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-indigo-700 disabled:opacity-50">
              Associate
            </button>
          </form>
        </div>

        {/* Variations Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6 lg:col-span-2">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Variations</h2>
            <button
              onClick={() => setShowVariation(true)}
              className="text-sm text-indigo-600 hover:text-indigo-800"
            >
              + Create Variation
            </button>
          </div>
          {garment.variations.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {garment.variations.map((v) => (
                <Link
                  key={v.id}
                  to={`/garments/${v.id}`}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
                >
                  <span className="font-medium text-sm">{v.name}</span>
                  <Badge label={v.lifecycle_stage} />
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-gray-400 text-sm">No variations.</p>
          )}
        </div>
      </div>

      {/* Create Variation Modal */}
      <Modal isOpen={showVariation} onClose={() => setShowVariation(false)} title="Create Variation">
        <form onSubmit={handleCreateVariation}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={varName}
              onChange={(e) => setVarName(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder={`${garment.name} (Long Sleeve)`}
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={varDesc}
              onChange={(e) => setVarDesc(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={3}
            />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setShowVariation(false)} className="px-4 py-2 text-sm text-gray-600">Cancel</button>
            <button type="submit" disabled={createVariationMutation.isPending} className="bg-indigo-600 text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50">
              {createVariationMutation.isPending ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
