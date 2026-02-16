import { useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { useGarments, useCreateGarment, useDeleteGarment } from "../hooks/useGarments";
import { LIFECYCLE_STAGES } from "../types";
import type { LifecycleStage } from "../types";
import { Badge } from "../components/ui/Badge";
import { Modal } from "../components/ui/Modal";
import { Spinner } from "../components/ui/Spinner";

export function Dashboard() {
  const [stageFilter, setStageFilter] = useState<LifecycleStage | "">("");
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");

  const { data: garments, isLoading, error } = useGarments(stageFilter || undefined);
  const createMutation = useCreateGarment();
  const deleteMutation = useDeleteGarment();

  const handleCreate = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      await createMutation.mutateAsync({ name: newName.trim(), description: newDesc.trim() || undefined });
      toast.success("Garment created");
      setShowCreate(false);
      setNewName("");
      setNewDesc("");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  const handleDelete = async (id: number, name: string) => {
    if (!confirm(`Delete "${name}"?`)) return;
    try {
      await deleteMutation.mutateAsync(id);
      toast.success("Garment deleted");
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "An error occurred");
    }
  };

  if (isLoading) return <Spinner />;
  if (error) return <div className="text-red-600">Error: {(error as Error).message}</div>;

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Garments</h1>
        <button
          onClick={() => setShowCreate(true)}
          className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm font-medium"
        >
          + New Garment
        </button>
      </div>

      {/* Stage filter tabs */}
      <div className="flex gap-2 mb-6 flex-wrap">
        <button
          onClick={() => setStageFilter("")}
          className={`px-3 py-1.5 rounded-full text-sm font-medium ${
            stageFilter === "" ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
          }`}
        >
          All
        </button>
        {LIFECYCLE_STAGES.map((stage) => (
          <button
            key={stage}
            onClick={() => setStageFilter(stage)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium ${
              stageFilter === stage ? "bg-indigo-600 text-white" : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {stage}
          </button>
        ))}
      </div>

      {/* Garment grid */}
      {garments && garments.length === 0 ? (
        <p className="text-gray-500">No garments found.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {garments?.map((g) => (
            <div key={g.id} className="bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <Link to={`/garments/${g.id}`} className="text-lg font-semibold text-gray-900 hover:text-indigo-600">
                  {g.name}
                </Link>
                <Badge label={g.lifecycle_stage} />
              </div>
              {g.description && (
                <p className="text-sm text-gray-500 mb-3 line-clamp-2">{g.description}</p>
              )}
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Created {new Date(g.created_at).toLocaleDateString()}</span>
                <button
                  onClick={() => handleDelete(g.id, g.name)}
                  className="text-red-400 hover:text-red-600"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create modal */}
      <Modal isOpen={showCreate} onClose={() => setShowCreate(false)} title="Create Garment">
        <form onSubmit={handleCreate}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="e.g. Summer Breeze Tee"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              className="w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="Optional description"
              rows={3}
            />
          </div>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={() => setShowCreate(false)} className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800">
              Cancel
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 text-sm font-medium disabled:opacity-50"
            >
              {createMutation.isPending ? "Creating..." : "Create"}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
