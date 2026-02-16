import { useQuery } from "@tanstack/react-query";
import * as api from "../lib/api";

export function useSuppliers() {
  return useQuery({
    queryKey: ["suppliers"],
    queryFn: api.getSuppliers,
  });
}
