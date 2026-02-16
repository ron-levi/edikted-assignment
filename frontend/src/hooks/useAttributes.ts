import { useQuery } from "@tanstack/react-query";
import * as api from "../lib/api";

export function useAttributes(category?: string) {
  return useQuery({
    queryKey: ["attributes", { category }],
    queryFn: () => api.getAttributes(category),
  });
}
