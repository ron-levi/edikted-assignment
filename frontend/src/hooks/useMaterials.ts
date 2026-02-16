import { useQuery } from "@tanstack/react-query";
import * as api from "../lib/api";

export function useMaterials() {
  return useQuery({
    queryKey: ["materials"],
    queryFn: api.getMaterials,
  });
}
